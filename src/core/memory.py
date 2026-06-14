"""
Управление памятью разговора
Conversation Memory Management
"""

from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json


@dataclass
class Message:
    """Сообщение в разговоре"""
    role: str  # "patient", "doctor", "agent"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConversationMemory:
    """
    Управление памятью разговора между агентом, врачом и пациентом
    """
    
    def __init__(self, max_history: int = 100):
        """
        Инициализация памяти
        
        Args:
            max_history: Максимальное количество сообщений в памяти
        """
        self.conversation: List[Message] = []
        self.max_history = max_history
        self.context_window = 10  # Количество последних сообщений для контекста
    
    def add_patient_message(self, content: str) -> None:
        """Добавить сообщение пациента"""
        self.conversation.append(Message(role="patient", content=content))
        self._trim_history()
    
    def add_doctor_message(self, content: str) -> None:
        """Добавить сообщение врача"""
        self.conversation.append(Message(role="doctor", content=content))
        self._trim_history()
    
    def add_agent_message(self, content: str, role: str = "agent") -> None:
        """Добавить сообщение агента"""
        self.conversation.append(Message(role=role, content=content))
        self._trim_history()
    
    def get_context(self, window_size: int = None) -> str:
        """
        Получить контекст для передачи в LLM
        
        Args:
            window_size: Количество последних сообщений (по умолчанию context_window)
            
        Returns:
            Отформатированный контекст
        """
        if window_size is None:
            window_size = self.context_window
        
        relevant_messages = self.conversation[-window_size:]
        
        context_parts = []
        for msg in relevant_messages:
            role_name = {
                "patient": "👤 Пациент",
                "doctor": "👨‍⚕️ Врач",
                "agent": "🤖 Агент",
                "interviewer": "🤖 Агент (интервью)"
            }.get(msg.role, msg.role)
            
            context_parts.append(f"{role_name}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def get_full_conversation(self) -> List[Dict[str, Any]]:
        """Получить полный разговор"""
        return [msg.to_dict() for msg in self.conversation]
    
    def get_patient_messages(self) -> List[str]:
        """Получить все сообщения пациента"""
        return [msg.content for msg in self.conversation if msg.role == "patient"]
    
    def get_symptoms_context(self) -> str:
        """Получить контекст симптомов из разговора"""
        patient_msgs = self.get_patient_messages()
        return " ".join(patient_msgs)
    
    def get_summary(self) -> Dict[str, Any]:
        """Получить резюме разговора"""
        return {
            "total_messages": len(self.conversation),
            "patient_messages": len([m for m in self.conversation if m.role == "patient"]),
            "doctor_messages": len([m for m in self.conversation if m.role == "doctor"]),
            "agent_messages": len([m for m in self.conversation if m.role == "agent"]),
            "started_at": self.conversation[0].timestamp if self.conversation else None,
            "last_message_at": self.conversation[-1].timestamp if self.conversation else None,
        }
    
    def _trim_history(self) -> None:
        """Обрезка истории при превышении лимита"""
        if len(self.conversation) > self.max_history:
            # Удаляем самые старые сообщения
            self.conversation = self.conversation[-self.max_history:]
    
    def reset(self) -> None:
        """Полный сброс памяти"""
        self.conversation = []
    
    def export_to_json(self) -> str:
        """Экспорт разговора в JSON"""
        return json.dumps(
            [msg.to_dict() for msg in self.conversation],
            ensure_ascii=False,
            indent=2
        )
    
    def export_to_file(self, filepath: str) -> None:
        """Экспорт разговора в файл"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.export_to_json())


