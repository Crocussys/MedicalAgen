"""
РЈРїСЂР°РІР»РµРЅРёРµ РїР°РјСЏС‚СЊСЋ СЂР°Р·РіРѕРІРѕСЂР°
Conversation Memory Management
"""

from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json


@dataclass
class Message:
    """РЎРѕРѕР±С‰РµРЅРёРµ РІ СЂР°Р·РіРѕРІРѕСЂРµ"""
    role: str  # "patient", "doctor", "agent"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConversationMemory:
    """
    РЈРїСЂР°РІР»РµРЅРёРµ РїР°РјСЏС‚СЊСЋ СЂР°Р·РіРѕРІРѕСЂР° РјРµР¶РґСѓ Р°РіРµРЅС‚РѕРј, РІСЂР°С‡РѕРј Рё РїР°С†РёРµРЅС‚РѕРј
    """
    
    def __init__(self, max_history: int = 100):
        """
        РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РїР°РјСЏС‚Рё
        
        Args:
            max_history: РњР°РєСЃРёРјР°Р»СЊРЅРѕРµ РєРѕР»РёС‡РµСЃС‚РІРѕ СЃРѕРѕР±С‰РµРЅРёР№ РІ РїР°РјСЏС‚Рё
        """
        self.conversation: List[Message] = []
        self.max_history = max_history
        self.context_window = 10  # РљРѕР»РёС‡РµСЃС‚РІРѕ РїРѕСЃР»РµРґРЅРёС… СЃРѕРѕР±С‰РµРЅРёР№ РґР»СЏ РєРѕРЅС‚РµРєСЃС‚Р°
    
    def add_patient_message(self, content: str) -> None:
        """Р”РѕР±Р°РІРёС‚СЊ СЃРѕРѕР±С‰РµРЅРёРµ РїР°С†РёРµРЅС‚Р°"""
        self.conversation.append(Message(role="patient", content=content))
        self._trim_history()
    
    def add_doctor_message(self, content: str) -> None:
        """Р”РѕР±Р°РІРёС‚СЊ СЃРѕРѕР±С‰РµРЅРёРµ РІСЂР°С‡Р°"""
        self.conversation.append(Message(role="doctor", content=content))
        self._trim_history()
    
    def add_agent_message(self, content: str, role: str = "agent") -> None:
        """Р”РѕР±Р°РІРёС‚СЊ СЃРѕРѕР±С‰РµРЅРёРµ Р°РіРµРЅС‚Р°"""
        self.conversation.append(Message(role=role, content=content))
        self._trim_history()
    
    def get_context(self, window_size: int = None) -> str:
        """
        РџРѕР»СѓС‡РёС‚СЊ РєРѕРЅС‚РµРєСЃС‚ РґР»СЏ РїРµСЂРµРґР°С‡Рё РІ LLM
        
        Args:
            window_size: РљРѕР»РёС‡РµСЃС‚РІРѕ РїРѕСЃР»РµРґРЅРёС… СЃРѕРѕР±С‰РµРЅРёР№ (РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ context_window)
            
        Returns:
            РћС‚С„РѕСЂРјР°С‚РёСЂРѕРІР°РЅРЅС‹Р№ РєРѕРЅС‚РµРєСЃС‚
        """
        if window_size is None:
            window_size = self.context_window
        
        relevant_messages = self.conversation[-window_size:]
        
        context_parts = []
        for msg in relevant_messages:
            role_name = {
                "patient": "рџ‘¤ РџР°С†РёРµРЅС‚",
                "doctor": "рџ‘ЁвЂЌвљ•пёЏ Р’СЂР°С‡",
                "agent": "рџ¤– РђРіРµРЅС‚",
                "interviewer": "рџ¤– РђРіРµРЅС‚ (РёРЅС‚РµСЂРІСЊСЋ)"
            }.get(msg.role, msg.role)
            
            context_parts.append(f"{role_name}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def get_full_conversation(self) -> List[Dict[str, Any]]:
        """РџРѕР»СѓС‡РёС‚СЊ РїРѕР»РЅС‹Р№ СЂР°Р·РіРѕРІРѕСЂ"""
        return [msg.to_dict() for msg in self.conversation]
    
    def get_patient_messages(self) -> List[str]:
        """РџРѕР»СѓС‡РёС‚СЊ РІСЃРµ СЃРѕРѕР±С‰РµРЅРёСЏ РїР°С†РёРµРЅС‚Р°"""
        return [msg.content for msg in self.conversation if msg.role == "patient"]
    
    def get_symptoms_context(self) -> str:
        """РџРѕР»СѓС‡РёС‚СЊ РєРѕРЅС‚РµРєСЃС‚ СЃРёРјРїС‚РѕРјРѕРІ РёР· СЂР°Р·РіРѕРІРѕСЂР°"""
        patient_msgs = self.get_patient_messages()
        return " ".join(patient_msgs)
    
    def get_summary(self) -> Dict[str, Any]:
        """РџРѕР»СѓС‡РёС‚СЊ СЂРµР·СЋРјРµ СЂР°Р·РіРѕРІРѕСЂР°"""
        return {
            "total_messages": len(self.conversation),
            "patient_messages": len([m for m in self.conversation if m.role == "patient"]),
            "doctor_messages": len([m for m in self.conversation if m.role == "doctor"]),
            "agent_messages": len([m for m in self.conversation if m.role == "agent"]),
            "started_at": self.conversation[0].timestamp if self.conversation else None,
            "last_message_at": self.conversation[-1].timestamp if self.conversation else None,
        }
    
    def _trim_history(self) -> None:
        """РћР±СЂРµР·РєР° РёСЃС‚РѕСЂРёРё РїСЂРё РїСЂРµРІС‹С€РµРЅРёРё Р»РёРјРёС‚Р°"""
        if len(self.conversation) > self.max_history:
            # РЈРґР°Р»СЏРµРј СЃР°РјС‹Рµ СЃС‚Р°СЂС‹Рµ СЃРѕРѕР±С‰РµРЅРёСЏ
            self.conversation = self.conversation[-self.max_history:]
    
    def reset(self) -> None:
        """РџРѕР»РЅС‹Р№ СЃР±СЂРѕСЃ РїР°РјСЏС‚Рё"""
        self.conversation = []
    
    def export_to_json(self) -> str:
        """Р­РєСЃРїРѕСЂС‚ СЂР°Р·РіРѕРІРѕСЂР° РІ JSON"""
        return json.dumps(
            [msg.to_dict() for msg in self.conversation],
            ensure_ascii=False,
            indent=2
        )
    
    def export_to_file(self, filepath: str) -> None:
        """Р­РєСЃРїРѕСЂС‚ СЂР°Р·РіРѕРІРѕСЂР° РІ С„Р°Р№Р»"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.export_to_json())


