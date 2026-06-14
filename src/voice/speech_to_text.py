"""
Р Р°СЃРїРѕР·РЅР°РІР°РЅРёРµ СЂРµС‡Рё (Speech-to-Text) СЃ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёРµРј Whisper
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
    Р Р°СЃРїРѕР·РЅР°РІР°РЅРёРµ СЂРµС‡Рё С‡РµСЂРµР· Whisper
    """
    
    def __init__(self, language: str = "uk"):
        """
        РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ СЂР°СЃРїРѕР·РЅР°РІР°С‚РµР»СЏ
        
        Args:
            language: РЇР·С‹Рє СЂР°СЃРїРѕР·РЅР°РІР°РЅРёСЏ (uk, ru, en)
        """
        self.language = language
        self.model = None
        self.is_listening = False
        self.sample_rate = 16000
        
        logger.info(f"рџЋ¤ РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ Whisper (РјРѕРґРµР»СЊ: {settings.whisper_model_size})")
        
        try:
            self.model = whisper.load_model(
                settings.whisper_model_size,
                device=settings.device
            )
            logger.info(f"вњ“ Whisper Р·Р°РіСЂСѓР¶РµРЅ СѓСЃРїРµС€РЅРѕ")
        except Exception as e:
            logger.error(f"вњ— РћС€РёР±РєР° Р·Р°РіСЂСѓР·РєРё Whisper: {e}")
            raise
    
    async def record_audio(
        self,
        duration: float = 10.0,
        callback: Optional[Callable] = None
    ) -> Optional[np.ndarray]:
        """
        Р—Р°РїРёСЃР°С‚СЊ Р°СѓРґРёРѕ СЃ РјРёРєСЂРѕС„РѕРЅР°
        
        Args:
            duration: Р”Р»РёС‚РµР»СЊРЅРѕСЃС‚СЊ Р·Р°РїРёСЃРё РІ СЃРµРєСѓРЅРґР°С…
            callback: Р¤СѓРЅРєС†РёСЏ РѕР±СЂР°С‚РЅРѕРіРѕ РІС‹Р·РѕРІР° РґР»СЏ РѕР±РЅРѕРІР»РµРЅРёСЏ СЃС‚Р°С‚СѓСЃР°
            
        Returns:
            РђСѓРґРёРѕРґР°РЅРЅС‹Рµ РІ РІРёРґРµ numpy array РёР»Рё None РµСЃР»Рё РѕС€РёР±РєР°
        """
        logger.info(f"рџЋ™пёЏ Р—Р°РїРёСЃСЊ Р°СѓРґРёРѕ ({duration} СЃРµРє)...")
        
        if callback:
            callback("recording", 0)
        
        try:
            # Р—Р°РїРёСЃС‹РІР°РµРј Р°СѓРґРёРѕ
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            )
            
            # Р–РґРµРј РѕРєРѕРЅС‡Р°РЅРёСЏ Р·Р°РїРёСЃРё
            sd.wait()
            
            if callback:
                callback("recording", 100)
            
            logger.info("вњ“ РђСѓРґРёРѕ Р·Р°РїРёСЃР°РЅРѕ")
            return audio
            
        except Exception as e:
            logger.error(f"вњ— РћС€РёР±РєР° Р·Р°РїРёСЃРё Р°СѓРґРёРѕ: {e}")
            return None
    
    async def recognize_from_file(self, audio_path: str) -> Optional[str]:
        """
        Р Р°СЃРїРѕР·РЅР°С‚СЊ СЂРµС‡СЊ РёР· С„Р°Р№Р»Р°
        
        Args:
            audio_path: РџСѓС‚СЊ Рє Р°СѓРґРёРѕС„Р°Р№Р»Сѓ
            
        Returns:
            Р Р°СЃРїРѕР·РЅР°РЅРЅС‹Р№ С‚РµРєСЃС‚ РёР»Рё None
        """
        try:
            logger.info(f"рџЋ¤ Р Р°СЃРїРѕР·РЅР°РІР°РЅРёРµ: {audio_path}")
            
            result = self.model.transcribe(
                audio_path,
                language=self.language,
                verbose=False
            )
            
            text = result.get("text", "").strip()
            
            if text:
                logger.info(f"вњ“ Р Р°СЃРїРѕР·РЅР°РЅРѕ: {text}")
            else:
                logger.warning("вљ пёЏ РўРµРєСЃС‚ РЅРµ СЂР°СЃРїРѕР·РЅР°РЅ")
            
            return text if text else None
            
        except Exception as e:
            logger.error(f"вњ— РћС€РёР±РєР° СЂР°СЃРїРѕР·РЅР°РІР°РЅРёСЏ: {e}")
            return None
    
    async def recognize_from_array(
        self,
        audio_array: np.ndarray
    ) -> Optional[str]:
        """
        Р Р°СЃРїРѕР·РЅР°С‚СЊ СЂРµС‡СЊ РёР· numpy array
        
        Args:
            audio_array: РђСѓРґРёРѕРґР°РЅРЅС‹Рµ
            
        Returns:
            Р Р°СЃРїРѕР·РЅР°РЅРЅС‹Р№ С‚РµРєСЃС‚ РёР»Рё None
        """
        try:
            # РЎРѕС…СЂР°РЅСЏРµРј РІСЂРµРјРµРЅРЅРѕ
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
                sf.write(temp_path, audio_array, self.sample_rate)
            
            # Р Р°СЃРїРѕР·РЅР°РµРј
            text = await self.recognize_from_file(temp_path)
            
            # РЈРґР°Р»СЏРµРј РІСЂРµРјРµРЅРЅС‹Р№ С„Р°Р№Р»
            Path(temp_path).unlink()
            
            return text
            
        except Exception as e:
            logger.error(f"вњ— РћС€РёР±РєР° СЂР°СЃРїРѕР·РЅР°РІР°РЅРёСЏ РёР· array: {e}")
            return None
    
    async def recognize_continuous(
        self,
        duration_per_chunk: float = 5.0,
        max_chunks: int = 10,
        callback: Optional[Callable] = None
    ) -> str:
        """
        РќРµРїСЂРµСЂС‹РІРЅРѕРµ СЂР°СЃРїРѕР·РЅР°РІР°РЅРёРµ СЃРѕ РјРЅРѕР¶РµСЃС‚РІРѕРј С„СЂР°РіРјРµРЅС‚РѕРІ
        
        Args:
            duration_per_chunk: Р”Р»РёС‚РµР»СЊРЅРѕСЃС‚СЊ РєР°Р¶РґРѕРіРѕ С„СЂР°РіРјРµРЅС‚Р°
            max_chunks: РњР°РєСЃРёРјР°Р»СЊРЅРѕРµ РєРѕР»РёС‡РµСЃС‚РІРѕ С„СЂР°РіРјРµРЅС‚РѕРІ
            callback: Р¤СѓРЅРєС†РёСЏ РѕР±СЂР°С‚РЅРѕРіРѕ РІС‹Р·РѕРІР°
            
        Returns:
            РџРѕР»СѓС‡РµРЅРЅС‹Р№ С‚РµРєСЃС‚
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
                    logger.info(f"Р¤СЂР°РіРјРµРЅС‚ {i+1}: {text}")
            
            # РџР°СѓР·Р° РјРµР¶РґСѓ С„СЂР°РіРјРµРЅС‚Р°РјРё
            await asyncio.sleep(0.5)
        
        return " ".join(full_text)
    
    def set_language(self, language: str):
        """РЈСЃС‚Р°РЅРѕРІРёС‚СЊ СЏР·С‹Рє СЂР°СЃРїРѕР·РЅР°РІР°РЅРёСЏ"""
        self.language = language
        logger.info(f"рџЊђ РЇР·С‹Рє СЂР°СЃРїРѕР·РЅР°РІР°РЅРёСЏ: {language}")


