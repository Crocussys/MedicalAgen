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
    
    def __init__(self, language: str = "ru"):
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
        """
        Распознать речь из numpy array
        
        Args:
            audio_array: Аудиоданные
            
        Returns:
            Распознанный текст или None
        """
        try:
            # Сохраняем временно
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
                sf.write(temp_path, audio_array, self.sample_rate)
            
            # Распознаем
            text = await self.recognize_from_file(temp_path)
            
            # Удаляем временный файл
            Path(temp_path).unlink()
            
            return text
            
        except Exception as e:
            logger.error(f"✗ Ошибка распознавания из array: {e}")
            return None
    
    async def recognize_continuous(
        self,
        duration_per_chunk: float = 5.0,
        max_chunks: int = 10,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Непрерывное распознавание со множеством фрагментов
        
        Args:
            duration_per_chunk: Длительность каждого фрагмента
            max_chunks: Максимальное количество фрагментов
            callback: Функция обратного вызова
            
        Returns:
            Полученный текст
        """
        full_text = []
        
        for i in range(max_chunks):
            if callback:
                callback(f"recording_chunk", (i + 1) * 100 // max_chunks)
            
            audio = await self.record_audio(duration_per_chunk, callback)
            
            if audio is not None:
                text = await self.recognize_from_array(audio)
                if text:
                    full_text.append(text)
                    logger.info(f"Фрагмент {i+1}: {text}")
            
            # Пауза между фрагментами
            await asyncio.sleep(0.5)
        
        return " ".join(full_text)
    
    def set_language(self, language: str):
        """Установить язык распознавания"""
        self.language = language
        logger.info(f"🌐 Язык распознавания: {language}")


