"""
Управление локальной LLM (Ollama)
LLM Manager for Ollama
"""

from typing import Optional, Dict, Any, List
import json
from datetime import datetime

import httpx
from loguru import logger

from config import settings


class LLMManager:
    """
    Менеджер для работы с локальной LLM (Ollama)
    """
    
    def __init__(self):
        """Инициализация менеджера LLM"""
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.embedding_model = settings.ollama_embedding_model
        self.client = httpx.AsyncClient(timeout=settings.ollama_timeout)
        self.system_prompt = self._build_system_prompt()
        
        logger.info(f"🧠 LLM Manager инициализирован")
        logger.info(f"   Модель: {self.model}")
        logger.info(f"   URL: {self.base_url}")
    
    def _build_system_prompt(self) -> str:
        """Построение системного промпта для медицинского агента"""
        return """Ты - профессиональный медицинский помощник, помогающий врачам диагностировать пациентов.

ИНСТРУКЦИИ:
1. Ты собираешь анамнез у пациента, задавая вопросы о его симптомах и медицинской истории
2. Ты помогаешь врачу анализировать информацию и предлагать диагнозы
3. Ты ВСЕГДА помнишь, что ты - ИИ помощник, а не врач
4. Ты НИКОГДА не даешь окончательные диагнозы без одобрения врача
5. Ты записываешь всю релевантную медицинскую информацию

ТОН:
- Профессиональный
- Эмпатичный к пациентам
- Сотрудничающий с врачами
- Четкий и понятный

ЯЗЫК:
- Используй простой, понятный язык для пациентов
- Используй медицинскую терминологию при общении с врачами
"""
    
    async def generate_response(
        self,
        context: str,
        task: str = "general",
        language: str = "uk",
        **kwargs
    ) -> str:
        """
        Генерация ответа от LLM
        
        Args:
            context: Контекст разговора
            task: Тип задачи (ask_medical_question, general, ask_clarification)
            language: Язык ответа
            **kwargs: Дополнительные параметры
            
        Returns:
            Сгенерированный ответ
        """
        prompt = self._build_prompt(context, task, language, **kwargs)
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": self.system_prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "num_predict": 500,
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                logger.debug(f"LLM response generated: {len(text)} chars")
                return text
            else:
                logger.error(f"LLM error: {response.status_code}")
                return "Извините, произошла ошибка при генерации ответа"
                
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "Произошла ошибка подключения к модели"
    
    async def extract_medical_info(self, text: str) -> Dict[str, Any]:
        """
        Извлечение медицинской информации из текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Словарь с извлеченной информацией
        """
        prompt = f"""Проанализируй следующий текст пациента и извлеки:
1. Симптомы (список)
2. Информацию о пациенте (возраст, пол, если указано)
3. Длительность симптомов
4. Интенсивность симптомов

Текст: "{text}"

Верни результат в формате JSON:
{{
    "symptoms": [...],
    "patient_info": {{...}},
    "duration": "...",
    "severity": "..."
}}
"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2,  # Низкая температура для точности
                }
            )
            
            if response.status_code == 200:
                text = response.json().get("response", "")
                # Пытаемся извлечь JSON
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = text[start:end]
                    return json.loads(json_str)
            
            return {"symptoms": [], "patient_info": {}}
            
        except Exception as e:
            logger.error(f"Error extracting medical info: {e}")
            return {"symptoms": [], "patient_info": {}}
    
    async def extract_command(self, text: str) -> str:
        """
        Извлечение команды из текста врача
        
        Args:
            text: Текст врача
            
        Returns:
            Команда (summarize, suggest_diagnosis, ask_follow_up, general)
        """
        prompt = f"""Какую команду хочет выполнить врач? 
Варианты: summarize, suggest_diagnosis, ask_follow_up, general

Текст: "{text}"

Ответь одним словом - названием команды."""
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.1,
                }
            )
            
            if response.status_code == 200:
                command = response.json().get("response", "").strip().lower()
                valid_commands = ["summarize", "suggest_diagnosis", "ask_follow_up", "general"]
                return command if command in valid_commands else "general"
            
            return "general"
            
        except Exception as e:
            logger.error(f"Error extracting command: {e}")
            return "general"
    
    def _build_prompt(
        self,
        context: str,
        task: str,
        language: str,
        **kwargs
    ) -> str:
        """Построение промпта для LLM"""
        
        task_prompts = {
            "ask_medical_question": f"""На основе следующего контекста разговора,
задай следующий медицинский вопрос для сбора анамнеза пациента.
Вопрос должен быть понятным и уточняющим.

Контекст: {context}

Задай один конкретный вопрос на {language} языке.""",
            
            "general": f"""Ответь на основе следующего контекста разговора:

Контекст: {context}

Дай краткий и полезный ответ на {language} языке.""",
            
            "ask_clarification": f"""На основе контекста, задай уточняющий вопрос 
для лучшего понимания симптомов:

Контекст: {context}

Задай один уточняющий вопрос на {language} языке.""",
        }
        
        return task_prompts.get(task, task_prompts["general"])
    
    async def close(self):
        """Закрытие клиента"""
        await self.client.aclose()
