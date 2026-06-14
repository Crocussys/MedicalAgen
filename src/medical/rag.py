"""
RAG СЃРёСЃС‚РµРјР° РґР»СЏ РјРµРґРёС†РёРЅСЃРєРѕРіРѕ Р°РіРµРЅС‚Р°
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
    """Р”РѕРєСѓРјРµРЅС‚ РІ Р±Р°Р·Рµ Р·РЅР°РЅРёР№"""
    id: str
    title: str
    content: str
    category: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


class MedicalKnowledgeBase:
    """
    РњРµРґРёС†РёРЅСЃРєР°СЏ Р±Р°Р·Р° Р·РЅР°РЅРёР№ РґР»СЏ RAG
    """
    
    def __init__(self):
        """РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ Р±Р°Р·С‹ Р·РЅР°РЅРёР№"""
        self.documents: List[Document] = []
        self.vector_store = {}
        self.loaded = False
        
        logger.info("рџ“љ РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РјРµРґРёС†РёРЅСЃРєРѕР№ Р±Р°Р·С‹ Р·РЅР°РЅРёР№")
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Р—Р°РіСЂСѓР·РёС‚СЊ Р±Р°Р·Сѓ Р·РЅР°РЅРёР№ РёР· С„Р°Р№Р»Р°
        
        Args:
            filepath: РџСѓС‚СЊ Рє С„Р°Р№Р»Сѓ Р±Р°Р·С‹ Р·РЅР°РЅРёР№
            
        Returns:
            True РµСЃР»Рё СѓСЃРїРµС€РЅРѕ
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for doc_data in data.get("documents", []):
                doc = Document(**doc_data)
                self.documents.append(doc)
            
            self.loaded = True
            logger.info(f"вњ“ Р—Р°РіСЂСѓР¶РµРЅРѕ {len(self.documents)} РґРѕРєСѓРјРµРЅС‚РѕРІ")
            return True
            
        except Exception as e:
            logger.error(f"вњ— РћС€РёР±РєР° Р·Р°РіСЂСѓР·РєРё Р‘Р—: {e}")
            return False
    
    def add_document(self, doc: Document):
        """Р”РѕР±Р°РІРёС‚СЊ РґРѕРєСѓРјРµРЅС‚ РІ Р‘Р—"""
        self.documents.append(doc)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Document]:
        """
        РџРѕРёСЃРє РґРѕРєСѓРјРµРЅС‚РѕРІ РїРѕ Р·Р°РїСЂРѕСЃСѓ
        
        Args:
            query: РџРѕРёСЃРєРѕРІС‹Р№ Р·Р°РїСЂРѕСЃ
            top_k: РљРѕР»РёС‡РµСЃС‚РІРѕ СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ
            category: Р¤РёР»СЊС‚СЂ РїРѕ РєР°С‚РµРіРѕСЂРёРё
            
        Returns:
            РЎРїРёСЃРѕРє РЅР°Р№РґРµРЅРЅС‹С… РґРѕРєСѓРјРµРЅС‚РѕРІ
        """
        # Р¤РёР»СЊС‚СЂСѓРµРј РїРѕ РєР°С‚РµРіРѕСЂРёРё РµСЃР»Рё РЅСѓР¶РЅРѕ
        candidates = self.documents
        if category:
            candidates = [d for d in candidates if d.category == category]
        
        # РџСЂРѕСЃС‚РѕР№ С‚РµРєСЃС‚РѕРІС‹Р№ РїРѕРёСЃРє (РІ СЂРµР°Р»СЊРЅРѕР№ СЃРёСЃС‚РµРјРµ РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ СЃРµРјР°РЅС‚РёС‡РµСЃРєРёР№ РїРѕРёСЃРє)
        scored_docs = []
        query_lower = query.lower()
        
        for doc in candidates:
            score = 0
            # РС‰РµРј СЃРѕРІРїР°РґРµРЅРёСЏ РІ Р·Р°РіРѕР»РѕРІРєРµ
            if query_lower in doc.title.lower():
                score += 2.0
            
            # РС‰РµРј СЃРѕРІРїР°РґРµРЅРёСЏ РІ РєРѕРЅС‚РµРЅС‚Рµ
            if query_lower in doc.content.lower():
                score += 1.0
            
            # РС‰РµРј СЃРѕРІРїР°РґРµРЅРёСЏ РІ РјРµС‚Р°РґР°РЅРЅС‹С…
            for key, value in doc.metadata.items():
                if isinstance(value, str) and query_lower in value.lower():
                    score += 0.5
            
            if score > 0:
                scored_docs.append((doc, score))
        
        # РЎРѕСЂС‚РёСЂСѓРµРј РїРѕ СЂРµР»РµРІР°РЅС‚РЅРѕСЃС‚Рё
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Р’РѕР·РІСЂР°С‰Р°РµРј top_k СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ
        return [doc for doc, score in scored_docs[:top_k]]
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """РџРѕР»СѓС‡РёС‚СЊ РєРѕРЅС‚РµРєСЃС‚ РґР»СЏ LLM РїРѕ Р·Р°РїСЂРѕСЃСѓ"""
        docs = self.search(query, top_k=top_k)
        
        if not docs:
            return ""
        
        context_parts = []
        for doc in docs:
            part = f"""
Р”РѕРєСѓРјРµРЅС‚: {doc.title}
РљР°С‚РµРіРѕСЂРёСЏ: {doc.category}
РЎРѕРґРµСЂР¶Р°РЅРёРµ: {doc.content[:500]}...
"""
            context_parts.append(part)
        
        return "\
---\
".join(context_parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """РџРѕР»СѓС‡РёС‚СЊ СЃС‚Р°С‚РёСЃС‚РёРєСѓ Р‘Р—"""
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
    РЎРёСЃС‚РµРјР° Retrieval-Augmented Generation РґР»СЏ Р°РіРµРЅС‚Р°
    """
    
    def __init__(self):
        """РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ RAG СЃРёСЃС‚РµРјС‹"""
        self.knowledge_base = MedicalKnowledgeBase()
        self.cache = {}
        
        logger.info("рџ”Ќ RAG СЃРёСЃС‚РµРјР° РёРЅРёС†РёР°Р»РёР·РёСЂРѕРІР°РЅР°")
    
    async def augment_context(
        self,
        query: str,
        base_context: str = ""
    ) -> str:
        """
        РџРѕРїРѕР»РЅРёС‚СЊ РєРѕРЅС‚РµРєСЃС‚ РёРЅС„РѕСЂРјР°С†РёРµР№ РёР· Р‘Р—
        
        Args:
            query: Р—Р°РїСЂРѕСЃ
            base_context: Р‘Р°Р·РѕРІС‹Р№ РєРѕРЅС‚РµРєСЃС‚
            
        Returns:
            Р Р°СЃС€РёСЂРµРЅРЅС‹Р№ РєРѕРЅС‚РµРєСЃС‚
        """
        # РС‰РµРј СЂРµР»РµРІР°РЅС‚РЅС‹Рµ РґРѕРєСѓРјРµРЅС‚С‹
        retrieved_context = self.knowledge_base.get_context_for_query(
            query,
            top_k=settings.top_k_results
        )
        
        if retrieved_context:
            return f"{base_context}\
\
рџ“љ Р РµР»РµРІР°РЅС‚РЅР°СЏ РёРЅС„РѕСЂРјР°С†РёСЏ РёР· Р‘Р—:\
{retrieved_context}"
        else:
            return base_context
    
    def load_knowledge_base(self, filepath: str) -> bool:
        """Р—Р°РіСЂСѓР·РёС‚СЊ Р±Р°Р·Сѓ Р·РЅР°РЅРёР№"""
        return self.knowledge_base.load_from_file(filepath)
    
    def get_kb_stats(self) -> Dict[str, Any]:
        """РџРѕР»СѓС‡РёС‚СЊ СЃС‚Р°С‚РёСЃС‚РёРєСѓ Р‘Р—"""
        return self.knowledge_base.get_statistics()

