"""
РЈРїСЂР°РІР»РµРЅРёРµ Р»РѕРєР°Р»СЊРЅРѕР№ LLM (Ollama)
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
    РњРµРЅРµРґР¶РµСЂ РґР»СЏ СЂР°Р±РѕС‚С‹ СЃ Р»РѕРєР°Р»СЊРЅРѕР№ LLM (Ollama)
    """
    
    def __init__(self):
        """РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РјРµРЅРµРґР¶РµСЂР° LLM"""
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.embedding_model = settings.ollama_embedding_model
        self.client = httpx.AsyncClient(timeout=settings.ollama_timeout)
        self.system_prompt = self._build_system_prompt()
        
        logger.info(f"рџ§  LLM Manager РёРЅРёС†РёР°Р»РёР·РёСЂРѕРІР°РЅ")
        logger.info(f"   РњРѕРґРµР»СЊ: {self.model}")
        logger.info(f"   URL: {self.base_url}")
    
    def _build_system_prompt(self) -> str:
        """РџРѕСЃС‚СЂРѕРµРЅРёРµ СЃРёСЃС‚РµРјРЅРѕРіРѕ РїСЂРѕРјРїС‚Р° РґР»СЏ РјРµРґРёС†РёРЅСЃРєРѕРіРѕ Р°РіРµРЅС‚Р°"""
        return """РўС‹ - РїСЂРѕС„РµСЃСЃРёРѕРЅР°Р»СЊРЅС‹Р№ РјРµРґРёС†РёРЅСЃРєРёР№ РїРѕРјРѕС‰РЅРёРє, РїРѕРјРѕРіР°СЋС‰РёР№ РІСЂР°С‡Р°Рј РґРёР°РіРЅРѕСЃС‚РёСЂРѕРІР°С‚СЊ РїР°С†РёРµРЅС‚РѕРІ.

РРќРЎРўР РЈРљР¦РР:
1. РўС‹ СЃРѕР±РёСЂР°РµС€СЊ Р°РЅР°РјРЅРµР· Сѓ РїР°С†РёРµРЅС‚Р°, Р·Р°РґР°РІР°СЏ РІРѕРїСЂРѕСЃС‹ Рѕ РµРіРѕ СЃРёРјРїС‚РѕРјР°С… Рё РјРµРґРёС†РёРЅСЃРєРѕР№ РёСЃС‚РѕСЂРёРё
2. РўС‹ РїРѕРјРѕРіР°РµС€СЊ РІСЂР°С‡Сѓ Р°РЅР°Р»РёР·РёСЂРѕРІР°С‚СЊ РёРЅС„РѕСЂРјР°С†РёСЋ Рё РїСЂРµРґР»Р°РіР°С‚СЊ РґРёР°РіРЅРѕР·С‹
3. РўС‹ Р’РЎР•Р“Р”Рђ РїРѕРјРЅРёС€СЊ, С‡С‚Рѕ С‚С‹ - РР РїРѕРјРѕС‰РЅРёРє, Р° РЅРµ РІСЂР°С‡
4. РўС‹ РќРРљРћР“Р”Рђ РЅРµ РґР°РµС€СЊ РѕРєРѕРЅС‡Р°С‚РµР»СЊРЅС‹Рµ РґРёР°РіРЅРѕР·С‹ Р±РµР· РѕРґРѕР±СЂРµРЅРёСЏ РІСЂР°С‡Р°
5. РўС‹ Р·Р°РїРёСЃС‹РІР°РµС€СЊ РІСЃСЋ СЂРµР»РµРІР°РЅС‚РЅСѓСЋ РјРµРґРёС†РёРЅСЃРєСѓСЋ РёРЅС„РѕСЂРјР°С†РёСЋ

РўРћРќ:
- РџСЂРѕС„РµСЃСЃРёРѕРЅР°Р»СЊРЅС‹Р№
- Р­РјРїР°С‚РёС‡РЅС‹Р№ Рє РїР°С†РёРµРЅС‚Р°Рј
- РЎРѕС‚СЂСѓРґРЅРёС‡Р°СЋС‰РёР№ СЃ РІСЂР°С‡Р°РјРё
- Р§РµС‚РєРёР№ Рё РїРѕРЅСЏС‚РЅС‹Р№

РЇР—Р«Рљ:
- РСЃРїРѕР»СЊР·СѓР№ РїСЂРѕСЃС‚РѕР№, РїРѕРЅСЏС‚РЅС‹Р№ СЏР·С‹Рє РґР»СЏ РїР°С†РёРµРЅС‚РѕРІ
- РСЃРїРѕР»СЊР·СѓР№ РјРµРґРёС†РёРЅСЃРєСѓСЋ С‚РµСЂРјРёРЅРѕР»РѕРіРёСЋ РїСЂРё РѕР±С‰РµРЅРёРё СЃ РІСЂР°С‡Р°РјРё
"""
    
    async def generate_response(
        self,
        context: str,
        task: str = "general",
        language: str = "uk",
        **kwargs
    ) -> str:
        """
        Р“РµРЅРµСЂР°С†РёСЏ РѕС‚РІРµС‚Р° РѕС‚ LLM
        
        Args:
            context: РљРѕРЅС‚РµРєСЃС‚ СЂР°Р·РіРѕРІРѕСЂР°
            task: РўРёРї Р·Р°РґР°С‡Рё (ask_medical_question, general, ask_clarification)
            language: РЇР·С‹Рє РѕС‚РІРµС‚Р°
            **kwargs: Р”РѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹Рµ РїР°СЂР°РјРµС‚СЂС‹
            
        Returns:
            РЎРіРµРЅРµСЂРёСЂРѕРІР°РЅРЅС‹Р№ РѕС‚РІРµС‚
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
                return "РР·РІРёРЅРёС‚Рµ, РїСЂРѕРёР·РѕС€Р»Р° РѕС€РёР±РєР° РїСЂРё РіРµРЅРµСЂР°С†РёРё РѕС‚РІРµС‚Р°"
                
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "РџСЂРѕРёР·РѕС€Р»Р° РѕС€РёР±РєР° РїРѕРґРєР»СЋС‡РµРЅРёСЏ Рє РјРѕРґРµР»Рё"
    
    async def extract_medical_info(self, text: str) -> Dict[str, Any]:
        """
        РР·РІР»РµС‡РµРЅРёРµ РјРµРґРёС†РёРЅСЃРєРѕР№ РёРЅС„РѕСЂРјР°С†РёРё РёР· С‚РµРєСЃС‚Р°
        
        Args:
            text: РўРµРєСЃС‚ РґР»СЏ Р°РЅР°Р»РёР·Р°
            
        Returns:
            РЎР»РѕРІР°СЂСЊ СЃ РёР·РІР»РµС‡РµРЅРЅРѕР№ РёРЅС„РѕСЂРјР°С†РёРµР№
        """
        prompt = f"""РџСЂРѕР°РЅР°Р»РёР·РёСЂСѓР№ СЃР»РµРґСѓСЋС‰РёР№ С‚РµРєСЃС‚ РїР°С†РёРµРЅС‚Р° Рё РёР·РІР»РµРєРё:
1. РЎРёРјРїС‚РѕРјС‹ (СЃРїРёСЃРѕРє)
2. РРЅС„РѕСЂРјР°С†РёСЋ Рѕ РїР°С†РёРµРЅС‚Рµ (РІРѕР·СЂР°СЃС‚, РїРѕР», РµСЃР»Рё СѓРєР°Р·Р°РЅРѕ)
3. Р”Р»РёС‚РµР»СЊРЅРѕСЃС‚СЊ СЃРёРјРїС‚РѕРјРѕРІ
4. РРЅС‚РµРЅСЃРёРІРЅРѕСЃС‚СЊ СЃРёРјРїС‚РѕРјРѕРІ

РўРµРєСЃС‚: "{text}"

Р’РµСЂРЅРё СЂРµР·СѓР»СЊС‚Р°С‚ РІ С„РѕСЂРјР°С‚Рµ JSON:
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
                    "temperature": 0.2,  # РќРёР·РєР°СЏ С‚РµРјРїРµСЂР°С‚СѓСЂР° РґР»СЏ С‚РѕС‡РЅРѕСЃС‚Рё
                }
            )
            
            if response.status_code == 200:
                text = response.json().get("response", "")
                # РџС‹С‚Р°РµРјСЃСЏ РёР·РІР»РµС‡СЊ JSON
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
        РР·РІР»РµС‡РµРЅРёРµ РєРѕРјР°РЅРґС‹ РёР· С‚РµРєСЃС‚Р° РІСЂР°С‡Р°
        
        Args:
            text: РўРµРєСЃС‚ РІСЂР°С‡Р°
            
        Returns:
            РљРѕРјР°РЅРґР° (summarize, suggest_diagnosis, ask_follow_up, general)
        """
        prompt = f"""РљР°РєСѓСЋ РєРѕРјР°РЅРґСѓ С…РѕС‡РµС‚ РІС‹РїРѕР»РЅРёС‚СЊ РІСЂР°С‡? 
Р’Р°СЂРёР°РЅС‚С‹: summarize, suggest_diagnosis, ask_follow_up, general

РўРµРєСЃС‚: "{text}"

РћС‚РІРµС‚СЊ РѕРґРЅРёРј СЃР»РѕРІРѕРј - РЅР°Р·РІР°РЅРёРµРј РєРѕРјР°РЅРґС‹."""
        
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
        """РџРѕСЃС‚СЂРѕРµРЅРёРµ РїСЂРѕРјРїС‚Р° РґР»СЏ LLM"""
        
        task_prompts = {
            "ask_medical_question": f"""РќР° РѕСЃРЅРѕРІРµ СЃР»РµРґСѓСЋС‰РµРіРѕ РєРѕРЅС‚РµРєСЃС‚Р° СЂР°Р·РіРѕРІРѕСЂР°,
Р·Р°РґР°Р№ СЃР»РµРґСѓСЋС‰РёР№ РјРµРґРёС†РёРЅСЃРєРёР№ РІРѕРїСЂРѕСЃ РґР»СЏ СЃР±РѕСЂР° Р°РЅР°РјРЅРµР·Р° РїР°С†РёРµРЅС‚Р°.
Р’РѕРїСЂРѕСЃ РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ РїРѕРЅСЏС‚РЅС‹Рј Рё СѓС‚РѕС‡РЅСЏСЋС‰РёРј.

РљРѕРЅС‚РµРєСЃС‚: {context}

Р—Р°РґР°Р№ РѕРґРёРЅ РєРѕРЅРєСЂРµС‚РЅС‹Р№ РІРѕРїСЂРѕСЃ РЅР° {language} СЏР·С‹РєРµ.""",
            
            "general": f"""РћС‚РІРµС‚СЊ РЅР° РѕСЃРЅРѕРІРµ СЃР»РµРґСѓСЋС‰РµРіРѕ РєРѕРЅС‚РµРєСЃС‚Р° СЂР°Р·РіРѕРІРѕСЂР°:

РљРѕРЅС‚РµРєСЃС‚: {context}

Р”Р°Р№ РєСЂР°С‚РєРёР№ Рё РїРѕР»РµР·РЅС‹Р№ РѕС‚РІРµС‚ РЅР° {language} СЏР·С‹РєРµ.""",
            
            "ask_clarification": f"""РќР° РѕСЃРЅРѕРІРµ РєРѕРЅС‚РµРєСЃС‚Р°, Р·Р°РґР°Р№ СѓС‚РѕС‡РЅСЏСЋС‰РёР№ РІРѕРїСЂРѕСЃ 
РґР»СЏ Р»СѓС‡С€РµРіРѕ РїРѕРЅРёРјР°РЅРёСЏ СЃРёРјРїС‚РѕРјРѕРІ:

РљРѕРЅС‚РµРєСЃС‚: {context}

Р—Р°РґР°Р№ РѕРґРёРЅ СѓС‚РѕС‡РЅСЏСЋС‰РёР№ РІРѕРїСЂРѕСЃ РЅР° {language} СЏР·С‹РєРµ.""",
        }
        
        return task_prompts.get(task, task_prompts["general"])
    
    async def close(self):
        """Р—Р°РєСЂС‹С‚РёРµ РєР»РёРµРЅС‚Р°"""
        await self.client.aclose()

