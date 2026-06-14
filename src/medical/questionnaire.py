"""
РђРЅРєРµС‚Р° РґР»СЏ СЃР±РѕСЂР° РёРЅС„РѕСЂРјР°С†РёРё Рѕ РїР°С†РёРµРЅС‚Рµ
Patient Questionnaire Module
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class QuestionnaireAnswer:
    """РћС‚РІРµС‚ РЅР° РІРѕРїСЂРѕСЃ Р°РЅРєРµС‚С‹"""
    question_id: str
    question_text: str
    answer: str
    category: str


class Questionnaire:
    """
    РЈРїСЂР°РІР»РµРЅРёРµ Р°РЅРєРµС‚РѕР№ РїР°С†РёРµРЅС‚Р°
    """
    
    def __init__(self, language: str = "uk"):
        """
        РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ Р°РЅРєРµС‚С‹
        
        Args:
            language: РЇР·С‹Рє Р°РЅРєРµС‚С‹
        """
        self.language = language
        self.questions = self._load_questions()
        self.answers: List[QuestionnaireAnswer] = []
        self.current_question_index = 0
    
    def _load_questions(self) -> List[Dict[str, Any]]:
        """Р—Р°РіСЂСѓР·РёС‚СЊ РІРѕРїСЂРѕСЃС‹ Р°РЅРєРµС‚С‹"""
        questions = [
            {
                "id": "age",
                "text": {
                    "uk": "РЎРєС–Р»СЊРєРё РІР°Рј СЂРѕРєС–РІ?",
                    "ru": "РЎРєРѕР»СЊРєРѕ РІР°Рј Р»РµС‚?",
                    "en": "How old are you?"
                },
                "type": "number",
                "category": "demographics",
                "required": True
            },
            {
                "id": "gender",
                "text": {
                    "uk": "Р’Р°С€Р° СЃС‚Р°С‚СЊ?",
                    "ru": "Р’Р°С€ РїРѕР»?",
                    "en": "Your gender?"
                },
                "type": "select",
                "options": ["male", "female", "other"],
                "category": "demographics",
                "required": True
            },
            {
                "id": "main_complaint",
                "text": {
                    "uk": "РЇРєР° РІР°С€Р° РѕСЃРЅРѕРІРЅР° СЃРєР°СЂРіР°?",
                    "ru": "РљР°РєР°СЏ РІР°С€Р° РѕСЃРЅРѕРІРЅР°СЏ Р¶Р°Р»РѕР±Р°?",
                    "en": "What is your main complaint?"
                },
                "type": "text",
                "category": "symptoms",
                "required": True
            },
            {
                "id": "symptom_duration",
                "text": {
                    "uk": "РЇРє РґРѕРІРіРѕ Сѓ РІР°СЃ С†С– СЃРёРјРїС‚РѕРјРё?",
                    "ru": "РљР°Рє РґРѕР»РіРѕ Сѓ РІР°СЃ СЌС‚Рё СЃРёРјРїС‚РѕРјС‹?",
                    "en": "How long have you had these symptoms?"
                },
                "type": "select",
                "options": ["less_than_1_day", "1_3_days", "4_7_days", "1_2_weeks", "more_than_2_weeks"],
                "category": "symptoms",
                "required": True
            },
            {
                "id": "temperature",
                "text": {
                    "uk": "Р§Рё РїС–РґРІРёС‰РµРЅР° РІР°С€Р° С‚РµРјРїРµСЂР°С‚СѓСЂР°?",
                    "ru": "РџРѕРІС‹С€РµРЅР° Р»Рё РІР°С€Р° С‚РµРјРїРµСЂР°С‚СѓСЂР°?",
                    "en": "Do you have a fever?"
                },
                "type": "select",
                "options": ["no", "mild", "moderate", "high"],
                "category": "symptoms",
                "required": False
            },
            {
                "id": "other_symptoms",
                "text": {
                    "uk": "РЇРєС– С‰Рµз—‡з‹ЂСѓ РІР°СЃ С”?",
                    "ru": "РљР°РєРёРµ РµС‰Рµ СЃРёРјРїС‚РѕРјС‹ Сѓ РІР°СЃ РµСЃС‚СЊ?",
                    "en": "What other symptoms do you have?"
                },
                "type": "text",
                "category": "symptoms",
                "required": False
            },
            {
                "id": "allergies",
                "text": {
                    "uk": "Р§Рё Сѓ РІР°СЃ С” Р°Р»РµСЂРіС–С—?",
                    "ru": "Р•СЃС‚СЊ Р»Рё Сѓ РІР°СЃ Р°Р»Р»РµСЂРіРёРё?",
                    "en": "Do you have any allergies?"
                },
                "type": "text",
                "category": "medical_history",
                "required": False
            },
            {
                "id": "medications",
                "text": {
                    "uk": "РЇРєС– Р»С–РєРё РІРё РїСЂРёР№РјР°С”С‚Рµ?",
                    "ru": "РљР°РєРёРµ Р»РµРєР°СЂСЃС‚РІР° РІС‹ РїСЂРёРЅРёРјР°РµС‚Рµ?",
                    "en": "What medications are you taking?"
                },
                "type": "text",
                "category": "medical_history",
                "required": False
            },
            {
                "id": "chronic_diseases",
                "text": {
                    "uk": "Р§Рё Сѓ РІР°СЃ С” С…СЂРѕРЅС–С‡РЅС– Р·Р°С…РІРѕСЂСЋРІР°РЅРЅСЏ?",
                    "ru": "Р•СЃС‚СЊ Р»Рё Сѓ РІР°СЃ С…СЂРѕРЅРёС‡РµСЃРєРёРµ Р·Р°Р±РѕР»РµРІР°РЅРёСЏ?",
                    "en": "Do you have any chronic diseases?"
                },
                "type": "text",
                "category": "medical_history",
                "required": False
            },
        ]
        
        return questions
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """РџРѕР»СѓС‡РёС‚СЊ С‚РµРєСѓС‰РёР№ РІРѕРїСЂРѕСЃ"""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def get_question_text(self) -> str:
        """РџРѕР»СѓС‡РёС‚СЊ С‚РµРєСЃС‚ С‚РµРєСѓС‰РµРіРѕ РІРѕРїСЂРѕСЃР°"""
        question = self.get_current_question()
        if question:
            return question["text"].get(self.language, question["text"].get("en"))
        return ""
    
    def answer_current_question(self, answer: str) -> bool:
        """
        РћС‚РІРµС‚РёС‚СЊ РЅР° С‚РµРєСѓС‰РёР№ РІРѕРїСЂРѕСЃ
        
        Args:
            answer: РћС‚РІРµС‚ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ
            
        Returns:
            True РµСЃР»Рё СѓСЃРїРµС€РЅРѕ, False РµСЃР»Рё РѕС€РёР±РєР°
        """
        question = self.get_current_question()
        if not question:
            return False
        
        # Р’Р°Р»РёРґРёСЂСѓРµРј РѕС‚РІРµС‚
        if not self._validate_answer(question, answer):
            return False
        
        # РЎРѕС…СЂР°РЅСЏРµРј РѕС‚РІРµС‚
        self.answers.append(QuestionnaireAnswer(
            question_id=question["id"],
            question_text=self.get_question_text(),
            answer=answer,
            category=question["category"]
        ))
        
        self.current_question_index += 1
        return True
    
    def _validate_answer(self, question: Dict, answer: str) -> bool:
        """Р’Р°Р»РёРґРёСЂРѕРІР°С‚СЊ РѕС‚РІРµС‚"""
        if not answer and question.get("required"):
            return False
        
        if question["type"] == "number":
            try:
                int(answer)
                return True
            except ValueError:
                return False
        
        if question["type"] == "select":
            return answer in question.get("options", [])
        
        return True
    
    def is_complete(self) -> bool:
        """РџСЂРѕРІРµСЂРёС‚СЊ, Р·Р°РІРµСЂС€РµРЅР° Р»Рё Р°РЅРєРµС‚Р°"""
        return self.current_question_index >= len(self.questions)
    
    def get_answers(self) -> Dict[str, Any]:
        """РџРѕР»СѓС‡РёС‚СЊ РІСЃРµ РѕС‚РІРµС‚С‹"""
        result = {}
        for answer in self.answers:
            result[answer.question_id] = answer.answer
        return result
    
    def get_answers_by_category(self) -> Dict[str, Dict[str, str]]:
        """РџРѕР»СѓС‡РёС‚СЊ РѕС‚РІРµС‚С‹ РїРѕ РєР°С‚РµРіРѕСЂРёСЏРј"""
        result = {}
        for answer in self.answers:
            if answer.category not in result:
                result[answer.category] = {}
            result[answer.category][answer.question_id] = answer.answer
        return result
    
    def get_patient_info(self) -> Dict[str, Any]:
        """РџРѕР»СѓС‡РёС‚СЊ РёРЅС„РѕСЂРјР°С†РёСЋ Рѕ РїР°С†РёРµРЅС‚Рµ РёР· РѕС‚РІРµС‚РѕРІ"""
        answers = self.get_answers()
        return {
            "age": int(answers.get("age", 0)),
            "gender": answers.get("gender"),
            "main_complaint": answers.get("main_complaint"),
            "symptom_duration": answers.get("symptom_duration"),
            "temperature": answers.get("temperature"),
            "other_symptoms": answers.get("other_symptoms"),
            "allergies": answers.get("allergies"),
            "medications": answers.get("medications"),
            "chronic_diseases": answers.get("chronic_diseases"),
        }
    
    def reset(self):
        """РЎР±СЂРѕСЃРёС‚СЊ Р°РЅРєРµС‚Сѓ"""
        self.answers = []
        self.current_question_index = 0
    
    def export_to_json(self) -> str:
        """Р­РєСЃРїРѕСЂС‚РёСЂРѕРІР°С‚СЊ РѕС‚РІРµС‚С‹ РІ JSON"""
        return json.dumps({
            "patient_info": self.get_patient_info(),
            "answers": [asdict(a) for a in self.answers]
        }, ensure_ascii=False, indent=2)

