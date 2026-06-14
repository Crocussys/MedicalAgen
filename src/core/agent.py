"""
РћСЃРЅРѕРІРЅРѕР№ РєР»Р°СЃСЃ РјРµРґРёС†РёРЅСЃРєРѕРіРѕ Р°РіРµРЅС‚Р°
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


class AgentRole(str, Enum):
    """Р РѕР»СЊ Р°РіРµРЅС‚Р° РІ СЂР°Р·РіРѕРІРѕСЂРµ"""
    INTERVIEWER = "interviewer"  # РЎРѕР±РёСЂР°РµС‚ Р°РЅР°РјРЅРµР·
    ASSISTANT = "assistant"      # РџРѕРјРѕРіР°РµС‚ РІСЂР°С‡Сѓ
    TRANSLATOR = "translator"    # РџРµСЂРµРІРѕРґРёС‚ РјРµР¶РґСѓ РІСЂР°С‡РѕРј Рё РїР°С†РёРµРЅС‚РѕРј


class MedicalAgent:
    """
    РћСЃРЅРѕРІРЅРѕР№ РєР»Р°СЃСЃ РјРµРґРёС†РёРЅСЃРєРѕРіРѕ РР-РїРѕРјРѕС‰РЅРёРєР°
    """
    
    def __init__(self, debug: bool = False):
        """
        РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ Р°РіРµРЅС‚Р°
        
        Args:
            debug: Р’РєР»СЋС‡РёС‚СЊ СЂРµР¶РёРј РѕС‚Р»Р°РґРєРё
        """
        self.debug = debug
        self.initialized = False
        
        logger.info("рџљЂ РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РјРµРґРёС†РёРЅСЃРєРѕРіРѕ Р°РіРµРЅС‚Р°...")
        
        try:
            # РРЅРёС†РёР°Р»РёР·РёСЂСѓРµРј РєРѕРјРїРѕРЅРµРЅС‚С‹
            self.llm_manager = LLMManager()
            self.memory = ConversationMemory()
            self.medical_logic = MedicalLogic()
            
            # РўРµРєСѓС‰РёР№ СЃРµР°РЅСЃ
            self.current_session = {
                "id": datetime.now().isoformat(),
                "patient_info": {},
                "symptoms": [],
                "anamnesis": [],
                "role": AgentRole.INTERVIEWER,
            }
            
            self.initialized = True
            logger.info("вњ“ РђРіРµРЅС‚ СѓСЃРїРµС€РЅРѕ РёРЅРёС†РёР°Р»РёР·РёСЂРѕРІР°РЅ")
            
        except Exception as e:
            logger.error(f"вњ— РћС€РёР±РєР° РёРЅРёС†РёР°Р»РёР·Р°С†РёРё Р°РіРµРЅС‚Р°: {e}")
            raise
    
    async def process_patient_message(self, message: str) -> str:
        """
        РћР±СЂР°Р±РѕС‚РєР° СЃРѕРѕР±С‰РµРЅРёСЏ РѕС‚ РїР°С†РёРµРЅС‚Р°
        
        Args:
            message: РЎРѕРѕР±С‰РµРЅРёРµ РїР°С†РёРµРЅС‚Р°
            
        Returns:
            РћС‚РІРµС‚ Р°РіРµРЅС‚Р°
        """
        if not self.initialized:
            return "РћС€РёР±РєР°: РђРіРµРЅС‚ РЅРµ РёРЅРёС†РёР°Р»РёР·РёСЂРѕРІР°РЅ"
        
        logger.info(f"рџ‘¤ РџР°С†РёРµРЅС‚: {message}")
        
        # Р”РѕР±Р°РІР»СЏРµРј РІ РїР°РјСЏС‚СЊ
        self.memory.add_patient_message(message)
        
        # РћР±СЂР°Р±Р°С‚С‹РІР°РµРј РєР°Рє СЃР±РѕСЂ Р°РЅР°РјРЅРµР·Р°
        response = await self._collect_anamnesis(message)
        
        # Р”РѕР±Р°РІР»СЏРµРј РѕС‚РІРµС‚ РІ РїР°РјСЏС‚СЊ
        self.memory.add_agent_message(response, role="interviewer")
        
        logger.info(f"рџ¤– РђРіРµРЅС‚: {response}")
        
        return response
    
    async def process_doctor_message(self, message: str) -> str:
        """
        РћР±СЂР°Р±РѕС‚РєР° СЃРѕРѕР±С‰РµРЅРёСЏ РѕС‚ РІСЂР°С‡Р°
        
        Args:
            message: РЎРѕРѕР±С‰РµРЅРёРµ РІСЂР°С‡Р°
            
        Returns:
            РћС‚РІРµС‚ Р°РіРµРЅС‚Р°
        """
        if not self.initialized:
            return "РћС€РёР±РєР°: РђРіРµРЅС‚ РЅРµ РёРЅРёС†РёР°Р»РёР·РёСЂРѕРІР°РЅ"
        
        logger.info(f"рџ‘ЁвЂЌвљ•пёЏ Р’СЂР°С‡: {message}")
        
        # Р”РѕР±Р°РІР»СЏРµРј РІ РїР°РјСЏС‚СЊ
        self.memory.add_doctor_message(message)
        
        # РћР±СЂР°Р±Р°С‚С‹РІР°РµРј РєРѕРјР°РЅРґСѓ РІСЂР°С‡Р°
        response = await self._process_doctor_command(message)
        
        logger.info(f"рџ¤– РђРіРµРЅС‚: {response}")
        
        return response
    
    async def _collect_anamnesis(self, patient_message: str) -> str:
        """
        РЎР±РѕСЂ Р°РЅР°РјРЅРµР·Р° Сѓ РїР°С†РёРµРЅС‚Р°
        
        Args:
            patient_message: РЎРѕРѕР±С‰РµРЅРёРµ РїР°С†РёРµРЅС‚Р°
            
        Returns:
            РЎР»РµРґСѓСЋС‰РёР№ РІРѕРїСЂРѕСЃ РёР»Рё Р·Р°РєР»СЋС‡РµРЅРёРµ
        """
        # РР·РІР»РµРєР°РµРј РёРЅС„РѕСЂРјР°С†РёСЋ РёР· СЃРѕРѕР±С‰РµРЅРёСЏ
        extracted = await self.llm_manager.extract_medical_info(patient_message)
        
        # Р”РѕР±Р°РІР»СЏРµРј РІ Р°РЅР°РјРЅРµР·
        if extracted.get("symptoms"):
            self.current_session["symptoms"].extend(extracted["symptoms"])
        
        if extracted.get("patient_info"):
            self.current_session["patient_info"].update(extracted["patient_info"])
        
        # Р“РµРЅРµСЂРёСЂСѓРµРј СЃР»РµРґСѓСЋС‰РёР№ РІРѕРїСЂРѕСЃ
        response = await self.llm_manager.generate_response(
            context=self.memory.get_context(),
            task="ask_medical_question",
            language=settings.ui_language
        )
        
        return response
    
    async def _process_doctor_command(self, message: str) -> str:
        """
        РћР±СЂР°Р±РѕС‚РєР° РєРѕРјР°РЅРґС‹ РІСЂР°С‡Р°
        
        Args:
            message: РљРѕРјР°РЅРґР° РІСЂР°С‡Р°
            
        Returns:
            Р РµР·СѓР»СЊС‚Р°С‚ РѕР±СЂР°Р±РѕС‚РєРё
        """
        # РђРЅР°Р»РёР·РёСЂСѓРµРј РєРѕРјР°РЅРґСѓ
        command = await self.llm_manager.extract_command(message)
        
        if command == "summarize":
            return self._summarize_anamnesis()
        elif command == "suggest_diagnosis":
            return await self._suggest_diagnosis()
        elif command == "ask_follow_up":
            return await self._generate_followup_question(message)
        else:
            # РћР±С‹С‡РЅС‹Р№ РѕС‚РІРµС‚
            return await self.llm_manager.generate_response(
                context=self.memory.get_context(),
                task="general",
                language=settings.ui_language
            )
    
    def _summarize_anamnesis(self) -> str:
        """Р РµР·СЋРјРµ СЃРѕР±СЂР°РЅРЅРѕРіРѕ Р°РЅР°РјРЅРµР·Р°"""
        summary = {
            "patient": self.current_session.get("patient_info", {}),
            "symptoms": self.current_session.get("symptoms", []),
            "questions_asked": len(self.memory.conversation),
        }
        return json.dumps(summary, ensure_ascii=False, indent=2)
    
    async def _suggest_diagnosis(self) -> str:
        """РџСЂРµРґР»РѕР¶РµРЅРёРµ РІРѕР·РјРѕР¶РЅС‹С… РґРёР°РіРЅРѕР·РѕРІ"""
        suggestions = await self.medical_logic.suggest_diagnosis(
            symptoms=self.current_session.get("symptoms", []),
            patient_info=self.current_session.get("patient_info", {})
        )
        return json.dumps(suggestions, ensure_ascii=False, indent=2)
    
    async def _generate_followup_question(self, context: str) -> str:
        """Р“РµРЅРµСЂР°С†РёСЏ СѓС‚РѕС‡РЅСЏСЋС‰РµРіРѕ РІРѕРїСЂРѕСЃР°"""
        return await self.llm_manager.generate_response(
            context=context,
            task="ask_clarification",
            language=settings.ui_language
        )
    
    def get_session_info(self) -> Dict[str, Any]:
        """РџРѕР»СѓС‡РµРЅРёРµ РёРЅС„РѕСЂРјР°С†РёРё Рѕ С‚РµРєСѓС‰РµРј СЃРµР°РЅСЃРµ"""
        return {
            "session_id": self.current_session["id"],
            "patient_info": self.current_session["patient_info"],
            "symptoms_count": len(self.current_session["symptoms"]),
            "conversation_length": len(self.memory.conversation),
        }
    
    def reset_session(self):
        """РЎР±СЂРѕСЃ С‚РµРєСѓС‰РµРіРѕ СЃРµР°РЅСЃР°"""
        self.current_session = {
            "id": datetime.now().isoformat(),
            "patient_info": {},
            "symptoms": [],
            "anamnesis": [],
            "role": AgentRole.INTERVIEWER,
        }
        self.memory.reset()
        logger.info("вњ“ РЎРµР°РЅСЃ СЃР±СЂРѕС€РµРЅ")

