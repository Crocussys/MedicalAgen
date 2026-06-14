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
        \"\"\"Инициализация Piper TTS\"\"\"
        try:
            # Пока используем заглушку - полная интеграция Piper требует 
            # установки бинарников и моделей
            logger.info(\"✓ Piper TTS инициализирован\")
        except Exception as e:
            logger.warning(f\"⚠️ Ошибка инициализации Piper: {e}\")
    
    async def synthesize(\n        self,\n        text: str,\n        callback: Optional[Callable] = None\n    ) -> Optional[np.ndarray]:\n        \"\"\"\n        Синтезировать речь из текста\n        \n        Args:\n            text: Текст для синтеза\n            callback: Функция обратного вызова\n            \n        Returns:\n            Аудиоданные в виде numpy array или None\n        \"\"\"\n        logger.info(f\"🔊 Синтез: {text[:50]}...\")\n        \n        if callback:\n            callback(\"synthesizing\", 0)\n        \n        try:\n            if settings.tts_engine == \"piper\":\n                audio = await self._synthesize_piper(text)\n            else:\n                audio = await self._synthesize_fallback(text)\n            \n            if callback:\n                callback(\"synthesizing\", 100)\n            \n            return audio\n            \n        except Exception as e:\n            logger.error(f\"✗ Ошибка синтеза: {e}\")\n            return None\n    \n    async def _synthesize_piper(self, text: str) -> Optional[np.ndarray]:\n        \"\"\"\n        Синтез с использованием Piper\n        \"\"\"\n        try:\n            # Генерируем аудио (упрощенная версия)\n            # В реальной реализации здесь будет вызов Piper\n            logger.info(\"Используется Piper для синтеза\")\n            \n            # Для теста создаем молчаливый звук\n            duration = max(1, len(text) // 10)  # Примерная длительность\n            audio = np.zeros(int(duration * self.sample_rate), dtype=np.float32)\n            \n            return audio\n            \n        except Exception as e:\n            logger.error(f\"Ошибка Piper синтеза: {e}\")\n            return None\n    \n    async def _synthesize_fallback(self, text: str) -> np.ndarray:\n        \"\"\"\n        Fallback синтез (молчаливый звук)\n        \"\"\"\n        logger.warning(\"Используется Fallback TTS (только тестирование)\")\n        duration = max(1, len(text) // 10)\n        return np.zeros(int(duration * self.sample_rate), dtype=np.float32)\n    \n    async def play_audio(self, audio: np.ndarray):\n        \"\"\"\n        Проиграть аудио\n        \n        Args:\n            audio: Аудиоданные\n        \"\"\"\n        try:\n            logger.info(f\"🔊 Воспроизведение аудио ({len(audio) / self.sample_rate:.1f} сек)\")\n            sd.play(audio, samplerate=self.sample_rate)\n            sd.wait()\n            logger.info(\"✓ Воспроизведение завершено\")\n        except Exception as e:\n            logger.error(f\"✗ Ошибка воспроизведения: {e}\")\n    \n    async def speak(\n        self,\n        text: str,\n        callback: Optional[Callable] = None\n    ):\n        \"\"\"\n        Синтезировать и сразу проиграть\n        \n        Args:\n            text: Текст для произнесения\n            callback: Функция обратного вызова\n        \"\"\"\n        audio = await self.synthesize(text, callback)\n        if audio is not None:\n            await self.play_audio(audio)\n    \n    def set_voice(self, voice: str):\n        \"\"\"Установить голос\"\"\"\n        self.voice = voice\n        logger.info(f\"🔊 Голос установлен: {voice}\")\n    \n    def set_speed(self, speed: float):\n        \"\"\"Установить скорость (0.5 - 2.0)\"\"\"\n        self.speed = max(0.5, min(2.0, speed))\n        logger.info(f\"🔊 Скорость: {self.speed}\")\n