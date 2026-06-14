"""
Основной класс медицинского агента
Main Medical AI Agent Class
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import json
from pathlib import Path

from loguru import logger

from config import settings
from .llm_manager import LLMManager
from .memory import ConversationMemory
from .medical_logic import MedicalLogic
from medical.anamnesis import AnamnesisManager


class AgentRole(str, Enum):
    """Роль агента в разговоре"""
    INTERVIEWER = "interviewer"  # Собирает анамнез
    ASSISTANT = "assistant"      # Помогает врачу
    TRANSLATOR = "translator"    # Переводит между врачом и пациентом


class MedicalAgent:
    """
    Основной класс медицинского ИИ-помощника
    """
    
    def __init__(self, debug: bool = False):
        """
        Инициализация агента
        
        Args:
            debug: Включить режим отладки
        """
        self.debug = debug
        self.initialized = False
        
        logger.info("🚀 Инициализация медицинского агента...")
        
        try:
            # Инициализируем компоненты
            self.llm_manager = LLMManager()
            self.memory = ConversationMemory()
            self.medical_logic = MedicalLogic()
            self.anamnesis = AnamnesisManager()
            
            # Текущий сеанс
            self.current_session = {
                "id": datetime.now().isoformat(),
                "patient_info": {},
                "symptoms": [],
                "anamnesis": [],
                "role": AgentRole.INTERVIEWER,
            }
            
            self.initialized = True
            logger.info("✓ Агент успешно инициализирован")
            
        except Exception as e:
            logger.error(f"✗ Ошибка инициализации агента: {e}")
            raise
    
    async def process_patient_message(self, message: str) -> str:
        """
        Обработка сообщения от пациента
        
        Args:
            message: Сообщение пациента
            
        Returns:
            Ответ агента
        """
        if not self.initialized:
            return "Ошибка: Агент не инициализирован"
        
        extracted = await self.llm_manager.extract_anamnesis_fields(message)

        logger.info(f"EXTRACTED: {extracted}")

        if not any(v is not None for v in extracted.values()):
            field = self.anamnesis.get_next_field()

            if field:
                extracted = {field: message}

        self.anamnesis.update(extracted)

        logger.info(f"ANAMNESIS: {self.anamnesis.to_dict()}")

        next_question = self.anamnesis.get_next_question()
        return next_question
    
    async def process_doctor_message(self, message: str) -> str:
        """
        Обработка сообщения от врача
        
        Args:
            message: Сообщение врача
            
        Returns:
            Ответ агента
        """
        if not self.initialized:
            return "Ошибка: Агент не инициализирован"
        
        logger.info(f"👨‍⚕️ Врач: {message}")
        
        # Добавляем в память
        self.memory.add_doctor_message(message)

        if "свод" in message.lower() or "анамнез" in message.lower():
            response = json.dumps(
                {
                    "anamnesis": self.anamnesis.to_dict()
                },
                ensure_ascii=False,
                indent=2
            )
        elif "не хватает" in message.lower():
            missing = self.anamnesis.get_missing_fields()
            response = json.dumps(
                {
                    "missing_fields": missing
                },
                ensure_ascii=False,
                indent=2
            )
        else:
            # Обрабатываем команду врача
            response = await self._process_doctor_command(message)
        
        logger.info(f"🤖 Агент: {response}")
        
        return response
    
    async def _collect_anamnesis(self, patient_message: str) -> str:
        """
        Сбор анамнеза у пациента
        
        Args:
            patient_message: Сообщение пациента
            
        Returns:
            Следующий вопрос или заключение
        """
        # Извлекаем информацию из сообщения
        extracted = await self.llm_manager.extract_medical_info(patient_message)
        
        # Добавляем в анамнез
        if extracted.get("symptoms"):
            self.current_session["symptoms"].extend(extracted["symptoms"])
        
        if extracted.get("patient_info"):
            self.current_session["patient_info"].update(extracted["patient_info"])
        
        # Генерируем следующий вопрос
        response = await self.llm_manager.generate_response(
            context=self.memory.get_context(),
            task="ask_medical_question",
            language=settings.ui_language
        )
        
        return response
    
    async def _process_doctor_command(self, message: str) -> str:
        """
        Обработка команды врача
        
        Args:
            message: Команда врача
            
        Returns:
            Результат обработки
        """
        # Анализируем команду
        command = await self.llm_manager.extract_command(message)
        
        if command == "summarize":
            return self._summarize_anamnesis()
        elif command == "suggest_diagnosis":
            return await self._suggest_diagnosis()
        elif command == "ask_follow_up":
            return await self._generate_followup_question(message)
        else:
            # Обычный ответ
            return await self.llm_manager.generate_response(
                context=self.memory.get_context(),
                task="general",
                language=settings.ui_language
            )
    
    def _summarize_anamnesis(self) -> str:
        """Резюме собранного анамнеза"""
        summary = {
            "patient": self.current_session.get("patient_info", {}),
            "symptoms": self.current_session.get("symptoms", []),
            "questions_asked": len(self.memory.conversation),
        }
        return json.dumps(summary, ensure_ascii=False, indent=2)
    
    async def _suggest_diagnosis(self) -> str:
        """Предложение возможных диагнозов"""
        suggestions = await self.medical_logic.suggest_diagnosis(
            symptoms=self.current_session.get("symptoms", []),
            patient_info=self.current_session.get("patient_info", {})
        )
        return json.dumps(suggestions, ensure_ascii=False, indent=2)
    
    async def _generate_followup_question(self, context: str) -> str:
        """Генерация уточняющего вопроса"""
        return await self.llm_manager.generate_response(
            context=context,
            task="ask_clarification",
            language=settings.ui_language
        )
    
    def get_session_info(self) -> Dict[str, Any]:
        """Получение информации о текущем сеансе"""
        return {
            "session_id": self.current_session["id"],
            "patient_info": self.current_session["patient_info"],
            "symptoms_count": len(self.current_session["symptoms"]),
            "conversation_length": len(self.memory.conversation),
        }
    
    def reset_session(self):
        """Сброс текущего сеанса"""
        self.current_session = {
            "id": datetime.now().isoformat(),
            "patient_info": {},
            "symptoms": [],
            "anamnesis": [],
            "role": AgentRole.INTERVIEWER,
        }
        self.memory.reset()
        logger.info("✓ Сеанс сброшен")

