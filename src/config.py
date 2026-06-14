"""
Конфигурация приложения
Application Configuration
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from dotenv import load_dotenv


# Загружаем .env файл
load_dotenv()


class Settings(BaseSettings):
    """Основные настройки приложения"""
    
    # Ollama LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_timeout: int = 300  # секунды
    
    # Whisper
    whisper_model_size: str = "base"  # tiny, base, small, medium, large
    device: str = "cpu"  # cpu, cuda
    
    # TTS
    tts_engine: str = "piper"  # piper, gtts
    tts_voice: str = "uk_UA-mykyta-x_low"
    tts_speed: float = 1.0
    
    # Приложение
    app_mode: str = "cli"  # cli, api, web
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = False
    
    # Пути
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = project_root / "data"
    medical_kb_path: Path = data_dir / "medical_kb"
    vectors_path: Path = data_dir / "vectors"
    models_dir: Path = project_root / "models"
    logs_dir: Path = project_root / "logs"
    
    # RAG
    chunk_size: int = 1000
    chunk_overlap: int = 100
    top_k_results: int = 3
    similarity_threshold: float = 0.7
    
    # Языки
    ui_language: str = "ru"  # uk, ru, en
    model_language: str = "ru"
    
    # Медицинские параметры
    max_anamnesis_questions: int = 20
    min_confidence_for_suggestion: float = 0.6

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "protected_namespaces": ()
    }
        
    def __init__(self, **data):
        super().__init__(**data)
        # Создаем необходимые директории
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)


# Создаем глобальный объект настроек
settings = Settings()

