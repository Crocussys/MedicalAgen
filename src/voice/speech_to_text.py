"""
Распознавание речи (Speech-to-Text) с использованием Whisper
Speech Recognition Module
"""

import asyncio
from typing import Optional, Callable
import tempfile
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper
from loguru import logger

from config import settings


class SpeechRecognizer:
    """
    Распознавание речи через Whisper
    """
    
    def __init__(self, language: str = "uk"):
        """
        Инициализация распознавателя
        
        Args:
            language: Язык распознавания (uk, ru, en)
        """
        self.language = language
        self.model = None
        self.is_listening = False
        self.sample_rate = 16000
        
        logger.info(f"🎤 Инициализация Whisper (модель: {settings.whisper_model_size})")
        
        try:
            self.model = whisper.load_model(
                settings.whisper_model_size,
                device=settings.device
            )
            logger.info(f"✓ Whisper загружен успешно")
        except Exception as e:
            logger.error(f"✗ Ошибка загрузки Whisper: {e}")
            raise
    
    async def record_audio(
        self,
        duration: float = 10.0,
        callback: Optional[Callable] = None
    ) -> Optional[np.ndarray]:
        """
        Записать аудио с микрофона
        
        Args:
            duration: Длительность записи в секундах
            callback: Функция обратного вызова для обновления статуса
            
        Returns:
            Аудиоданные в виде numpy array или None если ошибка
        """
        logger.info(f"🎙️ Запись аудио ({duration} сек)...")
        
        if callback:
            callback("recording", 0)
        
        try:
            # Записываем аудио
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            )
            
            # Ждем окончания записи
            sd.wait()
            
            if callback:
                callback("recording", 100)
            
            logger.info("✓ Аудио записано")
            return audio
            
        except Exception as e:
            logger.error(f"✗ Ошибка записи аудио: {e}")
            return None
    
    async def recognize_from_file(self, audio_path: str) -> Optional[str]:
        """
        Распознать речь из файла
        
        Args:
            audio_path: Путь к аудиофайлу
            
        Returns:
            Распознанный текст или None
        """
        try:
            logger.info(f"🎤 Распознавание: {audio_path}")
            
            result = self.model.transcribe(
                audio_path,
                language=self.language,
                verbose=False
            )
            
            text = result.get("text", "").strip()
            
            if text:
                logger.info(f"✓ Распознано: {text}")
            else:
                logger.warning("⚠️ Текст не распознан")
            
            return text if text else None
            
        except Exception as e:
            logger.error(f"✗ Ошибка распознавания: {e}")
            return None
    
    async def recognize_from_array(
        self,
        audio_array: np.ndarray
    ) -> Optional[str]:
        \"\"\"\n        Распознать речь из numpy array\n        \n        Args:\n            audio_array: Аудиоданные\n            \n        Returns:\n            Распознанный текст или None\n        \"\"\"\n        try:\n            # Сохраняем временно\n            with tempfile.NamedTemporaryFile(suffix=\".wav\", delete=False) as f:\n                temp_path = f.name\n                sf.write(temp_path, audio_array, self.sample_rate)\n            \n            # Распознаем\n            text = await self.recognize_from_file(temp_path)\n            \n            # Удаляем временный файл\n            Path(temp_path).unlink()\n            \n            return text\n            \n        except Exception as e:\n            logger.error(f\"✗ Ошибка распознавания из array: {e}\")\n            return None\n    \n    async def recognize_continuous(\n        self,\n        duration_per_chunk: float = 5.0,\n        max_chunks: int = 10,\n        callback: Optional[Callable] = None\n    ) -> str:\n        \"\"\"\n        Непрерывное распознавание со множеством фрагментов\n        \n        Args:\n            duration_per_chunk: Длительность каждого фрагмента\n            max_chunks: Максимальное количество фрагментов\n            callback: Функция обратного вызова\n            \n        Returns:\n            Полученный текст\n        \"\"\"\n        full_text = []\n        \n        for i in range(max_chunks):\n            if callback:\n                callback(f\"recording_chunk\", (i + 1) * 100 // max_chunks)\n            \n            audio = await self.record_audio(duration_per_chunk, callback)\n            \n            if audio is not None:\n                text = await self.recognize_from_array(audio)\n                if text:\n                    full_text.append(text)\n                    logger.info(f\"Фрагмент {i+1}: {text}\")\n            \n            # Пауза между фрагментами\n            await asyncio.sleep(0.5)\n        \n        return \" \".join(full_text)\n    \n    def set_language(self, language: str):\n        \"\"\"Установить язык распознавания\"\"\"\n        self.language = language\n        logger.info(f\"🌐 Язык распознавания: {language}\")\n