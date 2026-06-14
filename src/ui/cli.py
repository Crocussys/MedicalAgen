"""
Командная строка интерфейс
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


init(autoreset=True)  # Для цветного вывода на Windows


class CLIInterface:
    """
    Интерфейс командной строки для медицинского агента
    """
    
    def __init__(self, agent: MedicalAgent, voice_enabled: bool = False):
        """
        Инициализация CLI
        
        Args:
            agent: Экземпляр медицинского агента
            voice_enabled: Включить голосовой режим
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
                logger.info("✓ Голосовой режим включен")
            except Exception as e:
                logger.warning(f"⚠️ Голосовой режим недоступен: {e}")
                self.voice_enabled = False
    
    def run(self):
        """Запустить интерфейс"""
        self._show_welcome()
        asyncio.run(self._main_loop())
    
    def _show_welcome(self):
        """Показать приветствие"""
        print(f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════╗
║   {Fore.GREEN}Добро пожаловать в Медицинский ИИ-Помощник{Fore.CYAN}      ║
║   {Fore.YELLOW}Medical AI Assistant{Fore.CYAN}                                    ║
╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)
        
        print(f"{Fore.YELLOW}Доступные команды:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}/help{Style.RESET_ALL}           - Справка")
        print(f"  {Fore.GREEN}/patient{Style.RESET_ALL}        - Переключиться на режим пациента")
        print(f"  {Fore.GREEN}/doctor{Style.RESET_ALL}         - Переключиться на режим врача")
        print(f"  {Fore.GREEN}/voice{Style.RESET_ALL}          - Переключить голосовой режим")
        print(f"  {Fore.GREEN}/status{Style.RESET_ALL}         - Показать статус сеанса")
        print(f"  {Fore.GREEN}/clear{Style.RESET_ALL}          - Очистить память")
        print(f"  {Fore.GREEN}/exit{Style.RESET_ALL}           - Выход")
        print()
    
    async def _main_loop(self):
        """Главный цикл интерфейса"""
        while True:
            try:
                # Получаем ввод
                prompt = self._get_prompt()
                user_input = await self._get_user_input(prompt)
                
                if not user_input:
                    continue
                
                # Обрабатываем команды
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                    continue
                
                # Отправляем сообщение агенту
                if self.current_user == "patient":
                    response = await self.agent.process_patient_message(user_input)
                else:
                    response = await self.agent.process_doctor_message(user_input)
                
                # Выводим ответ
                self._print_response(response)
                
                # Если включен голос, проигрываем ответ
                if self.voice_enabled and self.text_to_speech:
                    await self.text_to_speech.speak(response)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Прервано пользователем{Style.RESET_ALL}")
                break
            except Exception as e:
                logger.error(f"Ошибка в главном цикле: {e}")
                print(f"{Fore.RED}✗ Ошибка: {e}{Style.RESET_ALL}")
    
    def _get_prompt(self) -> str:
        """Получить приглашение для ввода"""
        if self.current_user == "patient":
            return f"{Fore.CYAN}👤 Пациент{Style.RESET_ALL}> "
        else:
            return f"{Fore.MAGENTA}👨‍⚕️ Врач{Style.RESET_ALL}> "
    
    async def _get_user_input(self, prompt: str) -> str:
        """Получить ввод пользователя (текст или голос)"""
        if self.voice_enabled and self.speech_recognizer:
            print(f"{Fore.YELLOW}🎤 Говорите...{Style.RESET_ALL}")
            text = await self.speech_recognizer.record_audio(duration=10.0)
            if text:
                print(f"{Fore.CYAN}Распознано: {text}{Style.RESET_ALL}")
                return text
            else:
                print(f"{Fore.YELLOW}Попробуйте еще раз...{Style.RESET_ALL}")
                return ""
        else:
            return input(prompt).strip()
    
    def _print_response(self, response: str):
        \"\"\"Вывести ответ агента\"\"\"
        print(f\"{Fore.GREEN}🤖 Агент:{Style.RESET_ALL}\\n{response}\\n\")
    
    async def _handle_command(self, command: str):
        \"\"\"Обработать команду\"\"\"
        cmd = command.lower().strip()
        
        if cmd == \"/help\":
            self._show_help()
        
        elif cmd == \"/patient\":
            self.current_user = \"patient\"
            print(f\"{Fore.CYAN}➜ Режим: Пациент{Style.RESET_ALL}\")
        
        elif cmd == \"/doctor\":
            self.current_user = \"doctor\"
            print(f\"{Fore.CYAN}➜ Режим: Врач{Style.RESET_ALL}\")
        
        elif cmd == \"/voice\":
            if self.speech_recognizer and self.text_to_speech:
                self.voice_enabled = not self.voice_enabled
                status = f\"{Fore.GREEN}Включен{Style.RESET_ALL}\" if self.voice_enabled else f\"{Fore.RED}Отключен{Style.RESET_ALL}\"
                print(f\"🔊 Голосовой режим {status}\")
            else:
                print(f\"{Fore.RED}✗ Голосовой режим недоступен{Style.RESET_ALL}\")
        
        elif cmd == \"/status\":
            self._show_status()
        
        elif cmd == \"/clear\":
            self.agent.reset_session()
            print(f\"{Fore.CYAN}✓ Память очищена{Style.RESET_ALL}\")
        
        elif cmd == \"/exit\":
            print(f\"{Fore.YELLOW}До встречи!{Style.RESET_ALL}\")
            raise KeyboardInterrupt()
        
        else:
            print(f\"{Fore.YELLOW}❓ Неизвестная команда: {command}{Style.RESET_ALL}\")
    
    def _show_help(self):
        \"\"\"Показать справку\"\"\"
        print(f\"\"\"{Fore.CYAN}
╔════════════════════════════════════════════╗
║          {Fore.YELLOW}Справка{Fore.CYAN}                            ║
╚════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}Команды:{Style.RESET_ALL}
  /help       - Эта справка
  /patient    - Режим общения с пациентом
  /doctor     - Режим общения с врачом
  /voice      - Включить/отключить голос
  /status     - Показать статус сеанса
  /clear      - Очистить память
  /exit       - Выход

{Fore.GREEN}Использование:{Style.RESET_ALL}
  1. Выберите роль (/patient или /doctor)
  2. Вводите текст или говорите (если голос включен)
  3. Агент будет вам отвечать

{Fore.GREEN}Примеры:{Style.RESET_ALL}
  👤 Пациент> У меня болит горло и высокая температура
  👨‍⚕️ Врач> Какие еще симптомы?
        \"\"\")
    
    def _show_status(self):
        \"\"\"Показать статус сеанса\"\"\"
        info = self.agent.get_session_info()
        print(f\"\"\"{Fore.CYAN}
╔════════════════════════════════════════════╗
║         {Fore.YELLOW}Статус сеанса{Fore.CYAN}                     ║
╚════════════════════════════════════════════╝{Style.RESET_ALL}

  Текущий пользователь: {Fore.GREEN}{self.current_user}{Style.RESET_ALL}
  Голосовой режим:      {Fore.GREEN if self.voice_enabled else Fore.RED}{\"Включен\" if self.voice_enabled else \"Отключен\"}{Style.RESET_ALL}
  ID сеанса:            {Fore.YELLOW}{info['session_id'][:20]}...{Style.RESET_ALL}
  Симптомов:            {Fore.YELLOW}{info['symptoms_count']}{Style.RESET_ALL}
  Сообщений:            {Fore.YELLOW}{info['conversation_length']}{Style.RESET_ALL}
        \"\"\")
