"""
Медицинская логика для диагностики
Medical Logic for Diagnosis
"""

from typing import List, Dict, Any, Optional
import json
from dataclasses import dataclass


@dataclass
class DiagnosisSuggestion:
    """Предложение по диагнозу"""
    diagnosis: str
    confidence: float  # 0.0 - 1.0
    supporting_symptoms: List[str]
    additional_tests: List[str]
    notes: str


class MedicalLogic:
    """
    Медицинская логика для помощи в диагностике
    """
    
    def __init__(self):
        """Инициализация медицинской логики"""
        self.symptom_disease_mapping = self._load_symptom_mapping()
        self.disease_database = self._load_disease_database()
    
    async def suggest_diagnosis(
        self,
        symptoms: List[str],
        patient_info: Dict[str, Any],
        top_k: int = 5
    ) -> List[DiagnosisSuggestion]:
        """
        Предложить возможные диагнозы на основе симптомов
        
        Args:
            symptoms: Список симптомов
            patient_info: Информация о пациенте (возраст, пол, и т.д.)
            top_k: Количество лучших предложений
            
        Returns:
            Список предложений по диагнозам
        """
        if not symptoms:
            return []
        
        # Подсчитываем совпадения симптомов
        disease_scores = {}
        
        for symptom in symptoms:
            matching_diseases = self.symptom_disease_mapping.get(symptom.lower(), [])
            for disease, weight in matching_diseases:
                disease_scores[disease] = disease_scores.get(disease, 0) + weight
        
        # Сортируем по релевантности
        sorted_diseases = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Создаем предложения
        suggestions = []
        for disease, score in sorted_diseases[:top_k]:
            disease_info = self.disease_database.get(disease, {})
            
            # Вычисляем уверенность (нормализуем от 0 до 1)
            confidence = min(score / (len(symptoms) * 2), 1.0)
            
            # Фильтруем поддерживающие симптомы
            supporting = [
                s for s in symptoms
                if s.lower() in disease_info.get("common_symptoms", [])
            ]
            
            suggestion = DiagnosisSuggestion(
                diagnosis=disease,
                confidence=confidence,
                supporting_symptoms=supporting,
                additional_tests=disease_info.get("recommended_tests", []),
                notes=disease_info.get("notes", "")
            )
            
            suggestions.append(suggestion)
        
        return suggestions
    
    def _load_symptom_mapping(self) -> Dict[str, List[tuple]]:
        """
        Загрузить отображение симптомов на болезни
        Format: {"symptom": [("disease", weight), ...]}
        """
        return {
            "кашель": [("ОРВИ", 0.8), ("пневмония", 0.7), ("бронхит", 0.9), ("грипп", 0.8)],
            "температура": [("ОРВИ", 0.9), ("грипп", 0.95), ("пневмония", 0.8), ("ангина", 0.8)],
            "боль в горле": [("ангина", 0.95), ("ОРВИ", 0.7), ("фарингит", 0.9), ("грипп", 0.6)],
            "насморк": [("ОРВИ", 0.95), ("аллергия", 0.7), ("синусит", 0.6)],
            "чихание": [("аллергия", 0.8), ("ОРВИ", 0.6)],
            "головная боль": [("грипп", 0.8), ("мигрень", 0.7), ("менингит", 0.6)],
            "мышечная боль": [("грипп", 0.9), ("ОРВИ", 0.6), ("миозит", 0.7)],
            "усталость": [("анемия", 0.7), ("депрессия", 0.6), ("заболевания щитовидной железы", 0.6)],
            "одышка": [("астма", 0.8), ("пневмония", 0.7), ("сердечная недостаточность", 0.7)],
            "кровь в кашле": [("туберкулез", 0.8), ("рак легкого", 0.7), ("бронхоэктаз", 0.6)],
        }
    
    def _load_disease_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Загрузить базу данных болезней
        """
        return {
            "ОРВИ": {
                "name": "Острые респираторные вирусные инфекции",
                "common_symptoms": ["кашель", "температура", "насморк", "боль в горле"],
                "recommended_tests": ["клинический анализ крови", "ПЦР на вирусы"],
                "treatment": "Симптоматическое лечение, отдых, обильное питье",
                "notes": "Обычно вирусное заболевание, требует симптоматического лечения"
            },
            "грипп": {
                "name": "Грипп",
                "common_symptoms": ["температура", "головная боль", "мышечная боль", "кашель"],
                "recommended_tests": ["ПЦР на грипп", "клинический анализ крови"],
                "treatment": "Противовирусные препараты (Тамифлю), отдых",
                "notes": "Более серьезная вирусная инфекция, требует мониторинга"
            },
            "пневмония": {
                "name": "Пневмония",
                "common_symptoms": ["кашель", "температура", "одышка", "боль в груди"],
                "recommended_tests": ["рентген грудной клетки", "анализ мокроты"],
                "treatment": "Антибиотики, кислород если необходимо",
                "notes": "ТРЕБУЕТ врачебного наблюдения, может быть серьезным осложнением"
            },
            "ангина": {
                "name": "Острый фарингит/Ангина",
                "common_symptoms": ["боль в горле", "температура", "затруднение глотания"],
                "recommended_tests": ["мазок из зева", "клинический анализ крови"],
                "treatment": "Антибиотики (если бактериальная), полоскание, отдых",
                "notes": "Может быть вирусной или бактериальной"
            },
            "бронхит": {
                "name": "Бронхит",
                "common_symptoms": ["кашель", "температура", "мокрота"],
                "recommended_tests": ["рентген грудной клетки", "клинический анализ"],
                "treatment": "Отхаркивающие средства, отдых, теплое питье",
                "notes": "Может быть острым или хроническим"
            },
            "аллергия": {
                "name": "Аллергическая реакция",
                "common_symptoms": ["чихание", "насморк", "зуд"],
                "recommended_tests": ["аллергические пробы", "анализ на IgE"],
                "treatment": "Антигистаминные препараты, избегание аллергена",
                "notes": "Требует выявления аллергена"
            },
            "мигрень": {
                "name": "Мигрень",
                "common_symptoms": ["головная боль", "тошнота", "светобоязнь"],
                "recommended_tests": ["МРТ головного мозга"],
                "treatment": "Специфические противомигренозные препараты",
                "notes": "Хроническое состояние, требует специализированного лечения"
            },
            "астма": {
                "name": "Бронхиальная астма",
                "common_symptoms": ["одышка", "свистящее дыхание", "кашель"],
                "recommended_tests": ["спирометрия", "тест на реактивность дыхательных путей"],
                "treatment": "Ингаляторы, бронходилататоры, кортикостероиды",
                "notes": "Требует длительного управления и мониторинга"
            },
            "анемия": {
                "name": "Анемия",
                "common_symptoms": ["усталость", "бледность", "одышка"],
                "recommended_tests": ["общий анализ крови", "железо сыворотки", "витамин B12"],
                "treatment": "Железосодержащие препараты, витамины",
                "notes": "Могут быть разные причины, требует выяснения"
            },
            "туберкулез": {
                "name": "Туберкулез легких",
                "common_symptoms": ["кашель", "кровь в кашле", "потеря веса", "ночная потливость"],
                "recommended_tests": ["рентген легких", "туберкулиновая проба", "посев мокроты"],
                "treatment": "Противотуберкулезные препараты (долгий курс)",
                "notes": "ОПАСНОЕ ЗАБОЛЕВАНИЕ, требует немедленного врачебного вмешательства и изоляции"
            },
        }
    
    def get_disease_info(self, disease_name: str) -> Optional[Dict[str, Any]]:
        """Получить информацию о болезни"""
        return self.disease_database.get(disease_name)
    
    def validate_symptom(self, symptom: str) -> bool:
        """Проверить, является ли текст известным симптомом"""
        return symptom.lower() in self.symptom_disease_mapping
    
    def get_similar_symptoms(self, symptom: str) -> List[str]:
        """Получить похожие симптомы"""
        symptom_lower = symptom.lower()
        similar = []
        
        for known_symptom in self.symptom_disease_mapping.keys():
            # Простое сравнение по схожести
            if known_symptom.startswith(symptom_lower) or symptom_lower in known_symptom:
                similar.append(known_symptom)
        
        return similar

