"""
РљРѕРјР°РЅРґРЅР°СЏ СЃС‚СЂРѕРєР° РёРЅС‚РµСЂС„РµР№СЃ
Command Line Interface
"""

import asyncio
from typing import Optional
from colorama import init, Fore, Style

from loguru import logger

from core.agent import MedicalAgent
from voice.speech_to_text import SpeechRecognizer
from voice.text_to_speech import TextToSpeech
from config import settings


init(autoreset=True)  # Р”Р»СЏ С†РІРµС‚РЅРѕРіРѕ РІС‹РІРѕРґР° РЅР° Windows


class CLIInterface:
    """
    РРЅС‚РµСЂС„РµР№СЃ РєРѕРјР°РЅРґРЅРѕР№ СЃС‚СЂРѕРєРё РґР»СЏ РјРµРґРёС†РёРЅСЃРєРѕРіРѕ Р°РіРµРЅС‚Р°
    """
    
    def __init__(self, agent: MedicalAgent, voice_enabled: bool = False):
        """
        РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ CLI
        
        Args:
            agent: Р­РєР·РµРјРїР»СЏСЂ РјРµРґРёС†РёРЅСЃРєРѕРіРѕ Р°РіРµРЅС‚Р°
            voice_enabled: Р’РєР»СЋС‡РёС‚СЊ РіРѕР»РѕСЃРѕРІРѕР№ СЂРµР¶РёРј
        """
        self.agent = agent
        self.voice_enabled = voice_enabled
        self.speech_recognizer = None
        self.text_to_speech = None
        self.current_user = "patient"  # patient, doctor
        
        if voice_enabled:
            try:
                self.speech_recognizer = SpeechRecognizer(language=settings.ui_language)
                self.text_to_speech = TextToSpeech()
                logger.info("вњ“ Р“РѕР»РѕСЃРѕРІРѕР№ СЂРµР¶РёРј РІРєР»СЋС‡РµРЅ")
            except Exception as e:
                logger.warning(f"вљ пёЏ Р“РѕР»РѕСЃРѕРІРѕР№ СЂРµР¶РёРј РЅРµРґРѕСЃС‚СѓРїРµРЅ: {e}")
                self.voice_enabled = False
    
    def run(self):
        """Р—Р°РїСѓСЃС‚РёС‚СЊ РёРЅС‚РµСЂС„РµР№СЃ"""
        self._show_welcome()
        asyncio.run(self._main_loop())
    
    def _show_welcome(self):
        """РџРѕРєР°Р·Р°С‚СЊ РїСЂРёРІРµС‚СЃС‚РІРёРµ"""
        print(f"""
{Fore.CYAN}в•”в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•—
в•‘   {Fore.GREEN}Р”РѕР±СЂРѕ РїРѕР¶Р°Р»РѕРІР°С‚СЊ РІ РњРµРґРёС†РёРЅСЃРєРёР№ РР-РџРѕРјРѕС‰РЅРёРє{Fore.CYAN}      в•‘
в•‘   {Fore.YELLOW}Medical AI Assistant{Fore.CYAN}                                    в•‘
в•љв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ќ{Style.RESET_ALL}
        """)
        
        print(f"{Fore.YELLOW}Р”РѕСЃС‚СѓРїРЅС‹Рµ РєРѕРјР°РЅРґС‹:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}/help{Style.RESET_ALL}           - РЎРїСЂР°РІРєР°")
        print(f"  {Fore.GREEN}/patient{Style.RESET_ALL}        - РџРµСЂРµРєР»СЋС‡РёС‚СЊСЃСЏ РЅР° СЂРµР¶РёРј РїР°С†РёРµРЅС‚Р°")
        print(f"  {Fore.GREEN}/doctor{Style.RESET_ALL}         - РџРµСЂРµРєР»СЋС‡РёС‚СЊСЃСЏ РЅР° СЂРµР¶РёРј РІСЂР°С‡Р°")
        print(f"  {Fore.GREEN}/voice{Style.RESET_ALL}          - РџРµСЂРµРєР»СЋС‡РёС‚СЊ РіРѕР»РѕСЃРѕРІРѕР№ СЂРµР¶РёРј")
        print(f"  {Fore.GREEN}/status{Style.RESET_ALL}         - РџРѕРєР°Р·Р°С‚СЊ СЃС‚Р°С‚СѓСЃ СЃРµР°РЅСЃР°")
        print(f"  {Fore.GREEN}/clear{Style.RESET_ALL}          - РћС‡РёСЃС‚РёС‚СЊ РїР°РјСЏС‚СЊ")
        print(f"  {Fore.GREEN}/exit{Style.RESET_ALL}           - Р’С‹С…РѕРґ")
        print()
    
    async def _main_loop(self):
        """Р“Р»Р°РІРЅС‹Р№ С†РёРєР» РёРЅС‚РµСЂС„РµР№СЃР°"""
        while True:
            try:
                # РџРѕР»СѓС‡Р°РµРј РІРІРѕРґ
                prompt = self._get_prompt()
                user_input = await self._get_user_input(prompt)
                
                if not user_input:
                    continue
                
                # РћР±СЂР°Р±Р°С‚С‹РІР°РµРј РєРѕРјР°РЅРґС‹
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                    continue
                
                # РћС‚РїСЂР°РІР»СЏРµРј СЃРѕРѕР±С‰РµРЅРёРµ Р°РіРµРЅС‚Сѓ
                if self.current_user == "patient":
                    response = await self.agent.process_patient_message(user_input)
                else:
                    response = await self.agent.process_doctor_message(user_input)
                
                # Р’С‹РІРѕРґРёРј РѕС‚РІРµС‚
                self._print_response(response)
                
                # Р•СЃР»Рё РІРєР»СЋС‡РµРЅ РіРѕР»РѕСЃ, РїСЂРѕРёРіСЂС‹РІР°РµРј РѕС‚РІРµС‚
                if self.voice_enabled and self.text_to_speech:
                    await self.text_to_speech.speak(response)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}РџСЂРµСЂРІР°РЅРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»РµРј{Style.RESET_ALL}")
                break
            except Exception as e:
                logger.error(f"РћС€РёР±РєР° РІ РіР»Р°РІРЅРѕРј С†РёРєР»Рµ: {e}")
                print(f"{Fore.RED}вњ— РћС€РёР±РєР°: {e}{Style.RESET_ALL}")
    
    def _get_prompt(self) -> str:
        """РџРѕР»СѓС‡РёС‚СЊ РїСЂРёРіР»Р°С€РµРЅРёРµ РґР»СЏ РІРІРѕРґР°"""
        if self.current_user == "patient":
            return f"{Fore.CYAN}рџ‘¤ РџР°С†РёРµРЅС‚{Style.RESET_ALL}> "
        else:
            return f"{Fore.MAGENTA}рџ‘ЁвЂЌвљ•пёЏ Р’СЂР°С‡{Style.RESET_ALL}> "
    
    async def _get_user_input(self, prompt: str) -> str:
        """РџРѕР»СѓС‡РёС‚СЊ РІРІРѕРґ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ (С‚РµРєСЃС‚ РёР»Рё РіРѕР»РѕСЃ)"""
        if self.voice_enabled and self.speech_recognizer:
            print(f"{Fore.YELLOW}рџЋ¤ Р“РѕРІРѕСЂРёС‚Рµ...{Style.RESET_ALL}")
            text = await self.speech_recognizer.record_audio(duration=10.0)
            if text:
                print(f"{Fore.CYAN}Р Р°СЃРїРѕР·РЅР°РЅРѕ: {text}{Style.RESET_ALL}")
                return text
            else:
                print(f"{Fore.YELLOW}РџРѕРїСЂРѕР±СѓР№С‚Рµ РµС‰Рµ СЂР°Р·...{Style.RESET_ALL}")
                return ""
        else:
            return input(prompt).strip()
    
    def _print_response(self, response: str):
        """Р’С‹РІРµСЃС‚Рё РѕС‚РІРµС‚ Р°РіРµРЅС‚Р°"""
        print(f"{Fore.GREEN}рџ¤– РђРіРµРЅС‚:{Style.RESET_ALL}\
{response}\
")
    
    async def _handle_command(self, command: str):
        """РћР±СЂР°Р±РѕС‚Р°С‚СЊ РєРѕРјР°РЅРґСѓ"""
        cmd = command.lower().strip()
        
        if cmd == "/help":
            self._show_help()
        
        elif cmd == "/patient":
            self.current_user = "patient"
            print(f"{Fore.CYAN}вћњ Р РµР¶РёРј: РџР°С†РёРµРЅС‚{Style.RESET_ALL}")
        
        elif cmd == "/doctor":
            self.current_user = "doctor"
            print(f"{Fore.CYAN}вћњ Р РµР¶РёРј: Р’СЂР°С‡{Style.RESET_ALL}")
        
        elif cmd == "/voice":
            if self.speech_recognizer and self.text_to_speech:
                self.voice_enabled = not self.voice_enabled
                status = f"{Fore.GREEN}Р’РєР»СЋС‡РµРЅ{Style.RESET_ALL}" if self.voice_enabled else f"{Fore.RED}РћС‚РєР»СЋС‡РµРЅ{Style.RESET_ALL}"
                print(f"рџ”Љ Р“РѕР»РѕСЃРѕРІРѕР№ СЂРµР¶РёРј {status}")
            else:
                print(f"{Fore.RED}вњ— Р“РѕР»РѕСЃРѕРІРѕР№ СЂРµР¶РёРј РЅРµРґРѕСЃС‚СѓРїРµРЅ{Style.RESET_ALL}")
        
        elif cmd == "/status":
            self._show_status()
        
        elif cmd == "/clear":
            self.agent.reset_session()
            print(f"{Fore.CYAN}вњ“ РџР°РјСЏС‚СЊ РѕС‡РёС‰РµРЅР°{Style.RESET_ALL}")
        
        elif cmd == "/exit":
            print(f"{Fore.YELLOW}Р”Рѕ РІСЃС‚СЂРµС‡Рё!{Style.RESET_ALL}")
            raise KeyboardInterrupt()
        
        else:
            print(f"{Fore.YELLOW}вќ“ РќРµРёР·РІРµСЃС‚РЅР°СЏ РєРѕРјР°РЅРґР°: {command}{Style.RESET_ALL}")
    
    def _show_help(self):
        """РџРѕРєР°Р·Р°С‚СЊ СЃРїСЂР°РІРєСѓ"""
        print(f"""{Fore.CYAN}
в•”в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•—
в•‘          {Fore.YELLOW}РЎРїСЂР°РІРєР°{Fore.CYAN}                            в•‘
в•љв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ќ{Style.RESET_ALL}

{Fore.GREEN}РљРѕРјР°РЅРґС‹:{Style.RESET_ALL}
  /help       - Р­С‚Р° СЃРїСЂР°РІРєР°
  /patient    - Р РµР¶РёРј РѕР±С‰РµРЅРёСЏ СЃ РїР°С†РёРµРЅС‚РѕРј
  /doctor     - Р РµР¶РёРј РѕР±С‰РµРЅРёСЏ СЃ РІСЂР°С‡РѕРј
  /voice      - Р’РєР»СЋС‡РёС‚СЊ/РѕС‚РєР»СЋС‡РёС‚СЊ РіРѕР»РѕСЃ
  /status     - РџРѕРєР°Р·Р°С‚СЊ СЃС‚Р°С‚СѓСЃ СЃРµР°РЅСЃР°
  /clear      - РћС‡РёСЃС‚РёС‚СЊ РїР°РјСЏС‚СЊ
  /exit       - Р’С‹С…РѕРґ

{Fore.GREEN}РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ:{Style.RESET_ALL}
  1. Р’С‹Р±РµСЂРёС‚Рµ СЂРѕР»СЊ (/patient РёР»Рё /doctor)
  2. Р’РІРѕРґРёС‚Рµ С‚РµРєСЃС‚ РёР»Рё РіРѕРІРѕСЂРёС‚Рµ (РµСЃР»Рё РіРѕР»РѕСЃ РІРєР»СЋС‡РµРЅ)
  3. РђРіРµРЅС‚ Р±СѓРґРµС‚ РІР°Рј РѕС‚РІРµС‡Р°С‚СЊ

{Fore.GREEN}РџСЂРёРјРµСЂС‹:{Style.RESET_ALL}
  рџ‘¤ РџР°С†РёРµРЅС‚> РЈ РјРµРЅСЏ Р±РѕР»РёС‚ РіРѕСЂР»Рѕ Рё РІС‹СЃРѕРєР°СЏ С‚РµРјРїРµСЂР°С‚СѓСЂР°
  рџ‘ЁвЂЌвљ•пёЏ Р’СЂР°С‡> РљР°РєРёРµ РµС‰Рµ СЃРёРјРїС‚РѕРјС‹?
        """)
    
    def _show_status(self):
        """РџРѕРєР°Р·Р°С‚СЊ СЃС‚Р°С‚СѓСЃ СЃРµР°РЅСЃР°"""
        info = self.agent.get_session_info()
        print(f"""{Fore.CYAN}
в•”в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•—
в•‘         {Fore.YELLOW}РЎС‚Р°С‚СѓСЃ СЃРµР°РЅСЃР°{Fore.CYAN}                     в•‘
в•љв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ќ{Style.RESET_ALL}

  РўРµРєСѓС‰РёР№ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ: {Fore.GREEN}{self.current_user}{Style.RESET_ALL}
  Р“РѕР»РѕСЃРѕРІРѕР№ СЂРµР¶РёРј:      {Fore.GREEN if self.voice_enabled else Fore.RED}{"Р’РєР»СЋС‡РµРЅ" if self.voice_enabled else "РћС‚РєР»СЋС‡РµРЅ"}{Style.RESET_ALL}
  ID СЃРµР°РЅСЃР°:            {Fore.YELLOW}{info['session_id'][:20]}...{Style.RESET_ALL}
  РЎРёРјРїС‚РѕРјРѕРІ:            {Fore.YELLOW}{info['symptoms_count']}{Style.RESET_ALL}
  РЎРѕРѕР±С‰РµРЅРёР№:            {Fore.YELLOW}{info['conversation_length']}{Style.RESET_ALL}
        """)



