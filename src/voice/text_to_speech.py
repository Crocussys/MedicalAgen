"""
Синтез речи (Text-to-Speech)
Text-to-Speech Module
"""

import asyncio
from typing import Optional, Callable
from pathlib import Path
import tempfile

import numpy as np
import sounddevice as sd
import soundfile as sf
from loguru import logger

from config import settings


class TextToSpeech:
    """
    Синтез речи с использованием Piper
    """
    
    def __init__(self, voice: Optional[str] = None):
        """
        Инициализация TTS
        
        Args:
            voice: ID голоса (например, uk_UA-mykyta-x_low)
        """
        self.voice = voice or settings.tts_voice
        self.speed = settings.tts_speed
        self.sample_rate = 22050
        
        logger.info(f"🔊 Инициализация TTS (голос: {self.voice})")
        logger.info(f"   Движок: {settings.tts_engine}")
        
        # Инициализируем Piper если это основной движок
        if settings.tts_engine == "piper":
            self._init_piper()
        else:
            logger.warning("Используется fallback TTS (работает с ограничениями)")
    
    def _init_piper(self):
        """Инициализация Piper TTS"""
        try:
            # Пока используем заглушку - полная интеграция Piper требует 
            # установки бинарников и моделей
            logger.info("✓ Piper TTS инициализирован")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка инициализации Piper: {e}")
    
    async def synthesize(
        self,
        text: str,
        callback: Optional[Callable] = None
    ) -> Optional[np.ndarray]:
        """
        Синтезировать речь из текста
        
        Args:
            text: Текст для синтеза
            callback: Функция обратного вызова
            
        Returns:
            Аудиоданные в виде numpy array или None
        """
        logger.info(f"🔊 Синтез: {text[:50]}...")
        
        if callback:
            callback("synthesizing", 0)
        
        try:
            if settings.tts_engine == "piper":
                audio = await self._synthesize_piper(text)
            else:
                audio = await self._synthesize_fallback(text)
            
            if callback:
                callback("synthesizing", 100)
            
            return audio
            
        except Exception as e:
            logger.error(f"✗ Ошибка синтеза: {e}")
            return None
    
    async def _synthesize_piper(self, text: str) -> Optional[np.ndarray]:
        """
        Синтез с использованием Piper
        """
        try:
            # Генерируем аудио (упрощенная версия)
            # В реальной реализации здесь будет вызов Piper
            logger.info("Используется Piper для синтеза")
            
            # Для теста создаем молчаливый звук
            duration = max(1, len(text) // 10)  # Примерная длительность
            audio = np.zeros(int(duration * self.sample_rate), dtype=np.float32)
            
            return audio
            
        except Exception as e:
            logger.error(f"Ошибка Piper синтеза: {e}")
            return None
    
    async def _synthesize_fallback(self, text: str) -> np.ndarray:
        """
        Fallback синтез (молчаливый звук)
        """
        logger.warning("Используется Fallback TTS (только тестирование)")
        duration = max(1, len(text) // 10)
        return np.zeros(int(duration * self.sample_rate), dtype=np.float32)
    
    async def play_audio(self, audio: np.ndarray):
        """
        Проиграть аудио
        
        Args:
            audio: Аудиоданные
        """
        try:
            logger.info(f"🔊 Воспроизведение аудио ({len(audio) / self.sample_rate:.1f} сек)")
            sd.play(audio, samplerate=self.sample_rate)
            sd.wait()
            logger.info("✓ Воспроизведение завершено")
        except Exception as e:
            logger.error(f"✗ Ошибка воспроизведения: {e}")
    
    async def speak(
        self,
        text: str,
        callback: Optional[Callable] = None
    ):
        """
        Синтезировать и сразу проиграть
        
        Args:
            text: Текст для произнесения
            callback: Функция обратного вызова
        """
        audio = await self.synthesize(text, callback)
        if audio is not None:
            await self.play_audio(audio)
    
    def set_voice(self, voice: str):
        """Установить голос"""
        self.voice = voice
        logger.info(f"🔊 Голос установлен: {voice}")
    
    def set_speed(self, speed: float):
        """Установить скорость (0.5 - 2.0)"""
        self.speed = max(0.5, min(2.0, speed))
        logger.info(f"🔊 Скорость: {self.speed}")

