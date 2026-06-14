#!/usr/bin/env python3
"""
Скрипт установки и инициализации проекта
Setup and initialization script
"""

import sys
import subprocess
from pathlib import Path
import json


def run_command(cmd: list, description: str = "") -> bool:
    """Запустить команду"""
    if description:
        print(f"\n{'='*60}")
        print(f"▶ {description}")
        print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def create_directories() -> bool:
    """Создать необходимые директории"""
    dirs = [
        "data/medical_kb",
        "data/vectors",
        "logs",
        "models",
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"✓ Создана директория: {d}")
    
    return True


def setup_environment() -> bool:
    """Настроить окружение"""
    print("\n" + "="*60)
    print("▶ Подготовка окружения")
    print("="*60)
    
    # Копируем .env.example в .env
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        env_file.write_text(env_example.read_text())
        print("✓ Создан файл .env из .env.example")
    elif env_file.exists():
        print("✓ Файл .env уже существует")
    
    return True


def install_dependencies() -> bool:
    \"\"\"Установить Python зависимости\"\"\"
    return run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Установка Python зависимостей"
    )


def download_models() -> bool:
    \"\"\"Скачать модели Whisper и Ollama\"\"\"
    print("\n" + "="*60)
    print("▶ Загрузка моделей")
    print("="*60)
    
    try:
        # Загружаем Whisper модель
        print("\\nЗагрузка Whisper модели (может занять время)...")
        import whisper
        whisper.load_model("base")
        print("✓ Whisper модель загружена")
        
    except ImportError:
        print("⚠ Whisper еще не установлен, установите зависимости")
        return False
    except Exception as e:
        print(f"⚠ Ошибка загрузки Whisper: {e}")
    
    print("\nДля загрузки Ollama моделей:")
    print("  1. Установите Ollama: https://ollama.ai")
    print("  2. Запустите: ollama pull mistral")
    print("  3. Или запустите: ollama pull neural-chat")
    
    return True


def initialize_knowledge_base() -> bool:
    \"\"\"Инициализировать базу знаний\"\"\"
    print(\"\\n\" + \"=\"*60)
    print(\"▶ Инициализация медицинской базы знаний\")
    print(\"=\"*60)
    
    kb_file = Path(\"data/medical_kb/initial_knowledge_base.json\")
    
    if kb_file.exists():
        print(f\"✓ База знаний инициализирована: {kb_file}\")
        
        # Загружаем и выводим статистику
        try:
            with open(kb_file) as f:
                kb = json.load(f)
            doc_count = len(kb.get(\"documents\", []))
            print(f\"  Документов в БЗ: {doc_count}\")
        except Exception as e:
            print(f\"⚠ Ошибка чтения БЗ: {e}\")
    else:
        print(f\"⚠ Файл базы знаний не найден: {kb_file}\")
        return False
    
    return True


def verify_installation() -> bool:
    \"\"\"Проверить установку\"\"\"
    print(\"\\n\" + \"=\"*60)
    print(\"▶ Проверка установки\")
    print(\"=\"*60)
    
    checks = {
        \"Python 3.10+\": lambda: sys.version_info >= (3, 10),
        \"Файл requirements.txt\": lambda: Path(\"requirements.txt\").exists(),
        \"Файл main.py\": lambda: Path(\"main.py\").exists(),
        \"Директория src/\": lambda: Path(\"src\").exists(),
        \"Файл .env\": lambda: Path(\".env\").exists(),
        \"Директория data/\": lambda: Path(\"data\").exists(),
    }
    
    all_ok = True
    for check_name, check_func in checks.items():
        try:
            result = check_func()
            status = \"✓\" if result else \"✗\"
            print(f\"{status} {check_name}\")
            if not result:
                all_ok = False
        except Exception as e:
            print(f\"✗ {check_name}: {e}\")
            all_ok = False
    
    return all_ok


def main():
    \"\"\"Главная функция\"\"\"
    print(\"\"\"
╔═══════════════════════════════════════════════╗
║   Инициализация Медицинского ИИ-Помощника    ║
║   Setup - Medical AI Assistant                ║
╚═══════════════════════════════════════════════╝
    \"\"\")
    
    steps = [
        (\"Создание директорий\", create_directories),
        (\"Настройка окружения\", setup_environment),
        (\"Установка зависимостей\", install_dependencies),
        (\"Загрузка моделей\", download_models),
        (\"Инициализация БЗ\", initialize_knowledge_base),
        (\"Проверка установки\", verify_installation),
    ]
    
    completed = 0
    for step_name, step_func in steps:
        try:
            if step_func():
                completed += 1
            else:
                print(f\"\\n⚠ Шаг '{step_name}' завершился с предупреждением\")
        except Exception as e:
            print(f\"\\n✗ Ошибка на шаге '{step_name}': {e}\")
    
    # Итоги
    print(\"\\n\" + \"=\"*60)
    print(\"▶ ИТОГИ УСТАНОВКИ\")
    print(\"=\"*60)
    print(f\"✓ Завершено шагов: {completed}/{len(steps)}\")
    
    if completed == len(steps):
        print(\"\\n✓ Установка завершена успешно!\\n\")
        print(\"Дальнейшие шаги:\")
        print(\"  1. Убедитесь, что Ollama запущен: ollama serve\")
        print(\"  2. В другом терминале запустите приложение:\")
        print(\"     python main.py --mode cli          # Командная строка\")
        print(\"     python main.py --mode api          # REST API\")
        print(\"  3. Для голосового режима добавьте флаг --voice\")
        print(\"  4. Смотрите примеры: python examples.py\")
    else:
        print(\"\\n⚠ Установка завершена с предупреждениями\")\n        print(\"Проверьте логи выше и исправьте ошибки\")\n    
    print(\"=\"*60 + \"\\n\")


if __name__ == \"__main__\":\n    main()
