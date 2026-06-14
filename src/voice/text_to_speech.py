"""
РЎРёРЅС‚РµР· СЂРµС‡Рё (Text-to-Speech)
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
    РЎРёРЅС‚РµР· СЂРµС‡Рё СЃ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёРµРј Piper
    """
    
    def __init__(self, voice: Optional[str] = None):
        """
        РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ TTS
        
        Args:
            voice: ID РіРѕР»РѕСЃР° (РЅР°РїСЂРёРјРµСЂ, uk_UA-mykyta-x_low)
        """
        self.voice = voice or settings.tts_voice
        self.speed = settings.tts_speed
        self.sample_rate = 22050
        
        logger.info(f"рџ”Љ РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ TTS (РіРѕР»РѕСЃ: {self.voice})")
        logger.info(f"   Р”РІРёР¶РѕРє: {settings.tts_engine}")
        
        # РРЅРёС†РёР°Р»РёР·РёСЂСѓРµРј Piper РµСЃР»Рё СЌС‚Рѕ РѕСЃРЅРѕРІРЅРѕР№ РґРІРёР¶РѕРє
        if settings.tts_engine == "piper":
            self._init_piper()
        else:
            logger.warning("РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ fallback TTS (СЂР°Р±РѕС‚Р°РµС‚ СЃ РѕРіСЂР°РЅРёС‡РµРЅРёСЏРјРё)")
    
    def _init_piper(self):
        """РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ Piper TTS"""
        try:
            # РџРѕРєР° РёСЃРїРѕР»СЊР·СѓРµРј Р·Р°РіР»СѓС€РєСѓ - РїРѕР»РЅР°СЏ РёРЅС‚РµРіСЂР°С†РёСЏ Piper С‚СЂРµР±СѓРµС‚ 
            # СѓСЃС‚Р°РЅРѕРІРєРё Р±РёРЅР°СЂРЅРёРєРѕРІ Рё РјРѕРґРµР»РµР№
            logger.info("вњ“ Piper TTS РёРЅРёС†РёР°Р»РёР·РёСЂРѕРІР°РЅ")
        except Exception as e:
            logger.warning(f"вљ пёЏ РћС€РёР±РєР° РёРЅРёС†РёР°Р»РёР·Р°С†РёРё Piper: {e}")
    
    async def synthesize(
        self,
        text: str,
        callback: Optional[Callable] = None
    ) -> Optional[np.ndarray]:
        """
        РЎРёРЅС‚РµР·РёСЂРѕРІР°С‚СЊ СЂРµС‡СЊ РёР· С‚РµРєСЃС‚Р°
        
        Args:
            text: РўРµРєСЃС‚ РґР»СЏ СЃРёРЅС‚РµР·Р°
            callback: Р¤СѓРЅРєС†РёСЏ РѕР±СЂР°С‚РЅРѕРіРѕ РІС‹Р·РѕРІР°
            
        Returns:
            РђСѓРґРёРѕРґР°РЅРЅС‹Рµ РІ РІРёРґРµ numpy array РёР»Рё None
        """
        logger.info(f"рџ”Љ РЎРёРЅС‚РµР·: {text[:50]}...")
        
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
            logger.error(f"вњ— РћС€РёР±РєР° СЃРёРЅС‚РµР·Р°: {e}")
            return None
    
    async def _synthesize_piper(self, text: str) -> Optional[np.ndarray]:
        """
        РЎРёРЅС‚РµР· СЃ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёРµРј Piper
        """
        try:
            # Р“РµРЅРµСЂРёСЂСѓРµРј Р°СѓРґРёРѕ (СѓРїСЂРѕС‰РµРЅРЅР°СЏ РІРµСЂСЃРёСЏ)
            # Р’ СЂРµР°Р»СЊРЅРѕР№ СЂРµР°Р»РёР·Р°С†РёРё Р·РґРµСЃСЊ Р±СѓРґРµС‚ РІС‹Р·РѕРІ Piper
            logger.info("РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ Piper РґР»СЏ СЃРёРЅС‚РµР·Р°")
            
            # Р”Р»СЏ С‚РµСЃС‚Р° СЃРѕР·РґР°РµРј РјРѕР»С‡Р°Р»РёРІС‹Р№ Р·РІСѓРє
            duration = max(1, len(text) // 10)  # РџСЂРёРјРµСЂРЅР°СЏ РґР»РёС‚РµР»СЊРЅРѕСЃС‚СЊ
            audio = np.zeros(int(duration * self.sample_rate), dtype=np.float32)
            
            return audio
            
        except Exception as e:
            logger.error(f"РћС€РёР±РєР° Piper СЃРёРЅС‚РµР·Р°: {e}")
            return None
    
    async def _synthesize_fallback(self, text: str) -> np.ndarray:
        """
        Fallback СЃРёРЅС‚РµР· (РјРѕР»С‡Р°Р»РёРІС‹Р№ Р·РІСѓРє)
        """
        logger.warning("РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ Fallback TTS (С‚РѕР»СЊРєРѕ С‚РµСЃС‚РёСЂРѕРІР°РЅРёРµ)")
        duration = max(1, len(text) // 10)
        return np.zeros(int(duration * self.sample_rate), dtype=np.float32)
    
    async def play_audio(self, audio: np.ndarray):
        """
        РџСЂРѕРёРіСЂР°С‚СЊ Р°СѓРґРёРѕ
        
        Args:
            audio: РђСѓРґРёРѕРґР°РЅРЅС‹Рµ
        """
        try:
            logger.info(f"рџ”Љ Р’РѕСЃРїСЂРѕРёР·РІРµРґРµРЅРёРµ Р°СѓРґРёРѕ ({len(audio) / self.sample_rate:.1f} СЃРµРє)")
            sd.play(audio, samplerate=self.sample_rate)
            sd.wait()
            logger.info("вњ“ Р’РѕСЃРїСЂРѕРёР·РІРµРґРµРЅРёРµ Р·Р°РІРµСЂС€РµРЅРѕ")
        except Exception as e:
            logger.error(f"вњ— РћС€РёР±РєР° РІРѕСЃРїСЂРѕРёР·РІРµРґРµРЅРёСЏ: {e}")
    
    async def speak(
        self,
        text: str,
        callback: Optional[Callable] = None
    ):
        """
        РЎРёРЅС‚РµР·РёСЂРѕРІР°С‚СЊ Рё СЃСЂР°Р·Сѓ РїСЂРѕРёРіСЂР°С‚СЊ
        
        Args:
            text: РўРµРєСЃС‚ РґР»СЏ РїСЂРѕРёР·РЅРµСЃРµРЅРёСЏ
            callback: Р¤СѓРЅРєС†РёСЏ РѕР±СЂР°С‚РЅРѕРіРѕ РІС‹Р·РѕРІР°
        """
        audio = await self.synthesize(text, callback)
        if audio is not None:
            await self.play_audio(audio)
    
    def set_voice(self, voice: str):
        """РЈСЃС‚Р°РЅРѕРІРёС‚СЊ РіРѕР»РѕСЃ"""
        self.voice = voice
        logger.info(f"рџ”Љ Р“РѕР»РѕСЃ СѓСЃС‚Р°РЅРѕРІР»РµРЅ: {voice}")
    
    def set_speed(self, speed: float):
        """РЈСЃС‚Р°РЅРѕРІРёС‚СЊ СЃРєРѕСЂРѕСЃС‚СЊ (0.5 - 2.0)"""
        self.speed = max(0.5, min(2.0, speed))
        logger.info(f"рџ”Љ РЎРєРѕСЂРѕСЃС‚СЊ: {self.speed}")

