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
    """
    Медицинская база знаний для RAG
    """
    
    def __init__(self):
        """Инициализация базы знаний"""
        self.documents: List[Document] = []
        self.vector_store = {}
        self.loaded = False
        
        logger.info("📚 Инициализация медицинской базы знаний")
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Загрузить базу знаний из файла
        
        Args:
            filepath: Путь к файлу базы знаний
            
        Returns:
            True если успешно
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for doc_data in data.get("documents", []):
                doc = Document(**doc_data)
                self.documents.append(doc)
            
            self.loaded = True
            logger.info(f"✓ Загружено {len(self.documents)} документов")
            return True
            
        except Exception as e:
            logger.error(f"✗ Ошибка загрузки БЗ: {e}")
            return False
    
    def add_document(self, doc: Document):
        """Добавить документ в БЗ"""
        self.documents.append(doc)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Document]:
        """
        Поиск документов по запросу
        
        Args:
            query: Поисковый запрос
            top_k: Количество результатов
            category: Фильтр по категории
            
        Returns:
            Список найденных документов
        """
        # Фильтруем по категории если нужно
        candidates = self.documents
        if category:
            candidates = [d for d in candidates if d.category == category]
        
        # Простой текстовый поиск (в реальной системе используется семантический поиск)
        scored_docs = []
        query_lower = query.lower()
        
        for doc in candidates:
            score = 0
            # Ищем совпадения в заголовке
            if query_lower in doc.title.lower():
                score += 2.0
            
            # Ищем совпадения в контенте
            if query_lower in doc.content.lower():
                score += 1.0
            
            # Ищем совпадения в метаданных
            for key, value in doc.metadata.items():
                if isinstance(value, str) and query_lower in value.lower():
                    score += 0.5
            
            if score > 0:
                scored_docs.append((doc, score))
        
        # Сортируем по релевантности
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Возвращаем top_k результатов
        return [doc for doc, score in scored_docs[:top_k]]
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """Получить контекст для LLM по запросу"""
        docs = self.search(query, top_k=top_k)
        
        if not docs:
            return ""
        
        context_parts = []
        for doc in docs:
            part = f"""
Документ: {doc.title}
Категория: {doc.category}
Содержание: {doc.content[:500]}...
"""
            context_parts.append(part)
        
        return "\
---\
".join(context_parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику БЗ"""
        categories = {}
        for doc in self.documents:
            if doc.category not in categories:
                categories[doc.category] = 0
            categories[doc.category] += 1
        
        return {
            "total_documents": len(self.documents),
            "categories": categories,
            "loaded": self.loaded
        }


class RAGSystem:
    """
    Система Retrieval-Augmented Generation для агента
    """
    
    def __init__(self):
        """Инициализация RAG системы"""
        self.knowledge_base = MedicalKnowledgeBase()
        self.cache = {}
        
        logger.info("🔍 RAG система инициализирована")
    
    async def augment_context(
        self,
        query: str,
        base_context: str = ""
    ) -> str:
        """
        Пополнить контекст информацией из БЗ
        
        Args:
            query: Запрос
            base_context: Базовый контекст
            
        Returns:
            Расширенный контекст
        """
        # Ищем релевантные документы
        retrieved_context = self.knowledge_base.get_context_for_query(
            query,
            top_k=settings.top_k_results
        )
        
        if retrieved_context:
            return f"{base_context}\
\
📚 Релевантная информация из БЗ:\
{retrieved_context}"
        else:
            return base_context
    
    def load_knowledge_base(self, filepath: str) -> bool:
        """Загрузить базу знаний"""
        return self.knowledge_base.load_from_file(filepath)
    
    def get_kb_stats(self) -> Dict[str, Any]:
        """Получить статистику БЗ"""
        return self.knowledge_base.get_statistics()

