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

СТИЛЬ ВОПРОСОВ:
- Задавай вопросы простым русским языком.
- Не используй сложные медицинские обороты.
- Задавай не больше 1–2 вопросов за раз.
- Не пиши фразы вроде "имеет ли боль тошноту".
- Формулируй так: "Есть ли у вас тошнота?", "Есть ли диарея?", "Где именно болит?"
- Если пациент жалуется на боль в животе, сначала уточняй: локализацию, силу боли, длительность, температуру, тошноту, рвоту, стул.
"""
    
    async def generate_response(
        self,
        context: str,
        task: str = "general",
        language: str = "ru",
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
        prompt = f"""Проанализируй текст пациента и извлеки медицинскую информацию.

ВАЖНО:
- Отвечай только на русском языке.
- Названия симптомов пиши только на русском.
- Верни только JSON без пояснений.

Текст пациента: "{text}"

Формат:
{{
    "symptoms": [],
    "patient_info": {{}},
    "duration": "",
    "severity": ""
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
        
    async def extract_anamnesis_fields(
        self,
        text: str,
        current_question: str = ""
    ) -> dict:
        prompt = f"""
Извлеки данные анамнеза из текста пациента.

Верни только валидный JSON.
Не добавляй пояснений.
Не используй английский язык.
Если поле не указано в тексте, ставь null.

Поля:
- main_complaint
- duration
- severity
- temperature
- allergies
- medications
- chronic_diseases
- pain_location
- pain_character
- nausea
- vomiting
- stool
- movement_pain
- appetite

Текущий вопрос, на который отвечает пациент:
{current_question}

Текст пациента:
{text}

Пример ответа:
{{
  "main_complaint": null,
  "duration": null,
  "severity": null,
  "temperature": null,
  "allergies": null,
  "medications": null,
  "chronic_diseases": null,
  "pain_location": null,
  "pain_character": null,
  "nausea": null,
  "vomiting": null,
  "stool": null,
  "movement_pain": null,
  "appetite": null
}}

JSON:
"""

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
                text = response.json().get("response", "")
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(text[start:end])

            return {}

        except Exception as e:
            logger.error(f"Error extracting anamnesis fields: {e}")
            return {}
    
    def _build_prompt(
        self,
        context: str,
        task: str,
        language: str,
        **kwargs
    ) -> str:
        """Построение промпта для LLM"""

        language_names = {
            "ru": "русском",
            "uk": "украинском",
            "en": "английском",
        }
        language_name = language_names.get(language, "русском")

        task_prompts = {
            "ask_medical_question": f"""Ты собираешь анамнез у пациента.

Контекст разговора:
{context}

Правила:
- Отвечай только на русском языке.
- Задай только один короткий вопрос.
- Не повторяй уже заданные вопросы.
- Не ставь диагноз.
- Не перечисляй много симптомов сразу.
- При боли в животе уточняй по порядку: где болит, сила боли, когда началось, температура, тошнота/рвота, стул, усиливается ли при движении.

Следующий вопрос пациенту:""",
            
            "general": f"""Ответь на русском языке на основе контекста.

Контекст:
{context}

Правила:
- Отвечай кратко.
- Не используй английский и украинский язык.
- Если это пациент, задай один понятный уточняющий вопрос.

Ответ:""",
        }
        
        return task_prompts.get(task, task_prompts["general"])
    
    async def close(self):
        """Закрытие клиента"""
        await self.client.aclose()

