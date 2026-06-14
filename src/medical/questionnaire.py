"""
Анкета для сбора информации о пациенте
Patient Questionnaire Module
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class QuestionnaireAnswer:
    """Ответ на вопрос анкеты"""
    question_id: str
    question_text: str
    answer: str
    category: str


class Questionnaire:
    """
    Управление анкетой пациента
    """
    
    def __init__(self, language: str = "ru"):
        """
        Инициализация анкеты
        
        Args:
            language: Язык анкеты
        """
        self.language = language
        self.questions = self._load_questions()
        self.answers: List[QuestionnaireAnswer] = []
        self.current_question_index = 0
    
    def _load_questions(self) -> List[Dict[str, Any]]:
        """Загрузить вопросы анкеты"""
        questions = [
            {
                "id": "age",
                "text": {
                    "uk": "Скільки вам років?",
                    "ru": "Сколько вам лет?",
                    "en": "How old are you?"
                },
                "type": "number",
                "category": "demographics",
                "required": True
            },
            {
                "id": "gender",
                "text": {
                    "uk": "Ваша стать?",
                    "ru": "Ваш пол?",
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
                    "uk": "Яка ваша основна скарга?",
                    "ru": "Какая ваша основная жалоба?",
                    "en": "What is your main complaint?"
                },
                "type": "text",
                "category": "symptoms",
                "required": True
            },
            {
                "id": "symptom_duration",
                "text": {
                    "uk": "Як довго у вас ці симптоми?",
                    "ru": "Как долго у вас эти симптомы?",
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
                    "uk": "Чи підвищена ваша температура?",
                    "ru": "Повышена ли ваша температура?",
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
                    "uk": "Які ще症狀у вас є?",
                    "ru": "Какие еще симптомы у вас есть?",
                    "en": "What other symptoms do you have?"
                },
                "type": "text",
                "category": "symptoms",
                "required": False
            },
            {
                "id": "allergies",
                "text": {
                    "uk": "Чи у вас є алергії?",
                    "ru": "Есть ли у вас аллергии?",
                    "en": "Do you have any allergies?"
                },
                "type": "text",
                "category": "medical_history",
                "required": False
            },
            {
                "id": "medications",
                "text": {
                    "uk": "Які ліки ви приймаєте?",
                    "ru": "Какие лекарства вы принимаете?",
                    "en": "What medications are you taking?"
                },
                "type": "text",
                "category": "medical_history",
                "required": False
            },
            {
                "id": "chronic_diseases",
                "text": {
                    "uk": "Чи у вас є хронічні захворювання?",
                    "ru": "Есть ли у вас хронические заболевания?",
                    "en": "Do you have any chronic diseases?"
                },
                "type": "text",
                "category": "medical_history",
                "required": False
            },
        ]
        
        return questions
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Получить текущий вопрос"""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def get_question_text(self) -> str:
        """Получить текст текущего вопроса"""
        question = self.get_current_question()
        if question:
            return question["text"].get(self.language, question["text"].get("en"))
        return ""
    
    def answer_current_question(self, answer: str) -> bool:
        """
        Ответить на текущий вопрос
        
        Args:
            answer: Ответ пользователя
            
        Returns:
            True если успешно, False если ошибка
        """
        question = self.get_current_question()
        if not question:
            return False
        
        # Валидируем ответ
        if not self._validate_answer(question, answer):
            return False
        
        # Сохраняем ответ
        self.answers.append(QuestionnaireAnswer(
            question_id=question["id"],
            question_text=self.get_question_text(),
            answer=answer,
            category=question["category"]
        ))
        
        self.current_question_index += 1
        return True
    
    def _validate_answer(self, question: Dict, answer: str) -> bool:
        """Валидировать ответ"""
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
        """Проверить, завершена ли анкета"""
        return self.current_question_index >= len(self.questions)
    
    def get_answers(self) -> Dict[str, Any]:
        """Получить все ответы"""
        result = {}
        for answer in self.answers:
            result[answer.question_id] = answer.answer
        return result
    
    def get_answers_by_category(self) -> Dict[str, Dict[str, str]]:
        """Получить ответы по категориям"""
        result = {}
        for answer in self.answers:
            if answer.category not in result:
                result[answer.category] = {}
            result[answer.category][answer.question_id] = answer.answer
        return result
    
    def get_patient_info(self) -> Dict[str, Any]:
        """Получить информацию о пациенте из ответов"""
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
        """Сбросить анкету"""
        self.answers = []
        self.current_question_index = 0
    
    def export_to_json(self) -> str:
        """Экспортировать ответы в JSON"""
        return json.dumps({
            "patient_info": self.get_patient_info(),
            "answers": [asdict(a) for a in self.answers]
        }, ensure_ascii=False, indent=2)

