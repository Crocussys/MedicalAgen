#!/usr/bin/env python3
"""
Медицинский ИИ-Помощник - точка входа приложения
Medical AI Assistant - Application entry point
"""

import argparse
import sys
from pathlib import Path

# Добавляем src в path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import settings
from core.agent import MedicalAgent
from ui.cli import CLIInterface
from ui.api import start_api_server


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="Медицинский ИИ-Помощник с голосовым управлением"
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "api", "web"],
        default="cli",
        help="Режим работы приложения",
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Включить голосовой режим",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Режим отладки",
    )
    return parser.parse_args()


def main():
    """Основная функция"""
    args = parse_arguments()
    
    print(f"""
    ╔════════════════════════════════════════════════╗
    ║   Медицинский ИИ-Помощник                    ║
    ║   Medical AI Assistant                        ║
    ╚════════════════════════════════════════════════╝
    
    Режим: {args.mode}
    Голос: {'Включен' if args.voice else 'Отключен'}
    Отладка: {'Включена' if args.debug else 'Отключена'}
    """)

    try:
        # Инициализируем агента
        agent = MedicalAgent(debug=args.debug)
        
        if args.mode == "cli":
            # Командная строка
            cli = CLIInterface(agent, voice_enabled=args.voice)
            cli.run()
            
        elif args.mode == "api":
            # REST API
            start_api_server(agent, host=settings.app_host, port=settings.app_port)
            
        elif args.mode == "web":
            # Веб-интерфейс (будет реализован позже)
            print("Веб-интерфейс будет реализован в следующей версии")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n✓ Приложение завершено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
