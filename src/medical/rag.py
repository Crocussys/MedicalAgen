"""
RAG система для медицинского агента
Retrieval-Augmented Generation System
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import numpy as np
from dataclasses import dataclass

from loguru import logger
from config import settings


@dataclass
class Document:
    """Документ в базе знаний"""
    id: str
    title: str
    content: str
    category: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


class MedicalKnowledgeBase:
    \"\"\"
    Медицинская база знаний для RAG
    \"\"\"
    
    def __init__(self):
        \"\"\"Инициализация базы знаний\"\"\"
        self.documents: List[Document] = []
        self.vector_store = {}
        self.loaded = False
        
        logger.info(\"📚 Инициализация медицинской базы знаний\")
    
    def load_from_file(self, filepath: str) -> bool:
        \"\"\"
        Загрузить базу знаний из файла
        
        Args:
            filepath: Путь к файлу базы знаний
            
        Returns:
            True если успешно
        \"\"\"
        try:
            with open(filepath, \"r\", encoding=\"utf-8\") as f:
                data = json.load(f)
            
            for doc_data in data.get(\"documents\", []):
                doc = Document(**doc_data)
                self.documents.append(doc)
            
            self.loaded = True
            logger.info(f\"✓ Загружено {len(self.documents)} документов\")
            return True
            
        except Exception as e:
            logger.error(f\"✗ Ошибка загрузки БЗ: {e}\")
            return False
    
    def add_document(self, doc: Document):
        \"\"\"Добавить документ в БЗ\"\"\"
        self.documents.append(doc)
    
    def search(\n        self,\n        query: str,\n        top_k: int = 5,\n        category: Optional[str] = None\n    ) -> List[Document]:\n        \"\"\"\n        Поиск документов по запросу\n        \n        Args:\n            query: Поисковый запрос\n            top_k: Количество результатов\n            category: Фильтр по категории\n            \n        Returns:\n            Список найденных документов\n        \"\"\"\n        # Фильтруем по категории если нужно\n        candidates = self.documents\n        if category:\n            candidates = [d for d in candidates if d.category == category]\n        \n        # Простой текстовый поиск (в реальной системе используется семантический поиск)\n        scored_docs = []\n        query_lower = query.lower()\n        \n        for doc in candidates:\n            score = 0\n            # Ищем совпадения в заголовке\n            if query_lower in doc.title.lower():\n                score += 2.0\n            \n            # Ищем совпадения в контенте\n            if query_lower in doc.content.lower():\n                score += 1.0\n            \n            # Ищем совпадения в метаданных\n            for key, value in doc.metadata.items():\n                if isinstance(value, str) and query_lower in value.lower():\n                    score += 0.5\n            \n            if score > 0:\n                scored_docs.append((doc, score))\n        \n        # Сортируем по релевантности\n        scored_docs.sort(key=lambda x: x[1], reverse=True)\n        \n        # Возвращаем top_k результатов\n        return [doc for doc, score in scored_docs[:top_k]]\n    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        \"\"\"Получить контекст для LLM по запросу\"\"\"
        docs = self.search(query, top_k=top_k)\n        \n        if not docs:\n            return \"\"\n        \n        context_parts = []\n        for doc in docs:\n            part = f\"\"\"\nДокумент: {doc.title}\nКатегория: {doc.category}\nСодержание: {doc.content[:500]}...\n\"\"\"\n            context_parts.append(part)\n        \n        return \"\\n---\\n\".join(context_parts)\n    \n    def get_statistics(self) -> Dict[str, Any]:\n        \"\"\"Получить статистику БЗ\"\"\"
        categories = {}\n        for doc in self.documents:\n            if doc.category not in categories:\n                categories[doc.category] = 0\n            categories[doc.category] += 1\n        \n        return {\n            \"total_documents\": len(self.documents),\n            \"categories\": categories,\n            \"loaded\": self.loaded\n        }\n\n\nclass RAGSystem:\n    \"\"\"\n    Система Retrieval-Augmented Generation для агента\n    \"\"\"\n    \n    def __init__(self):\n        \"\"\"Инициализация RAG системы\"\"\"
        self.knowledge_base = MedicalKnowledgeBase()\n        self.cache = {}\n        \n        logger.info(\"🔍 RAG система инициализирована\")\n    \n    async def augment_context(\n        self,\n        query: str,\n        base_context: str = \"\"\n    ) -> str:\n        \"\"\"\n        Пополнить контекст информацией из БЗ\n        \n        Args:\n            query: Запрос\n            base_context: Базовый контекст\n            \n        Returns:\n            Расширенный контекст\n        \"\"\"\n        # Ищем релевантные документы\n        retrieved_context = self.knowledge_base.get_context_for_query(\n            query,\n            top_k=settings.top_k_results\n        )\n        \n        if retrieved_context:\n            return f\"{base_context}\\n\\n📚 Релевантная информация из БЗ:\\n{retrieved_context}\"\n        else:\n            return base_context\n    \n    def load_knowledge_base(self, filepath: str) -> bool:\n        \"\"\"Загрузить базу знаний\"\"\"
        return self.knowledge_base.load_from_file(filepath)\n    \n    def get_kb_stats(self) -> Dict[str, Any]:\n        \"\"\"Получить статистику БЗ\"\"\"
        return self.knowledge_base.get_statistics()\n