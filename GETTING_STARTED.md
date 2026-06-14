# 🚀 Медицинский ИИ-Помощник - Начало работы

## 📌 Что вы получили

```
✅ Полнофункциональный локальный ИИ-агент
✅ Голосовое управление (Whisper + Piper)
✅ Локальная LLM (Ollama - без интернета)
✅ Система сбора анамнеза
✅ RAG для медицинской БЗ
✅ REST API + CLI интерфейсы
✅ Docker поддержка
✅ Полная документация
```

## ⚡ Быстрый старт (5 минут)

### Шаг 1️⃣ - Установите Ollama

Скачайте с https://ollama.ai

```bash
# Проверка установки
ollama --version

# Загрузите модель
ollama pull mistral
```

### Шаг 2️⃣ - Установите зависимости

```bash
cd d:\Code\Repositories\MedicalAgent2

# Создайте виртуальное окружение (рекомендуется)
python -m venv venv
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 3️⃣ - Инициализируйте проект

```bash
python setup.py
```

### Шаг 4️⃣ - Запустите приложение

```bash
# Режим командной строки
python main.py --mode cli

# С голосом (если есть микрофон)
python main.py --mode cli --voice

# REST API режим
python main.py --mode api
```

## 📚 Документация

| Документ | Описание |
|----------|---------|
| [README.md](README.md) | Полное описание проекта |
| [QUICKSTART.md](QUICKSTART.md) | Быстрый старт |
| [INSTALLATION.md](INSTALLATION.md) | Подробная установка |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Архитектура системы |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Сводка компонентов |

## 🎮 Использование CLI

### Основные команды

```
👤 Пациент> У меня болит горло
🤖 Агент: Как долго у вас болит горло?

👤 Пациент> /doctor      ← Переключиться на врача
👨‍⚕️ Врач> Какие симптомы?
🤖 Агент: [ответ для врача]

👨‍⚕️ Врач> /suggest_diagnosis  ← Предложить диагнозы
🤖 Агент: Возможные диагнозы...

👨‍⚕️ Врач> /exit           ← Выход
```

### Полный список команд

```
/help       - Справка
/patient    - Режим пациента
/doctor     - Режим врача  
/voice      - Включить/отключить голос
/status     - Статус сеанса
/clear      - Очистить память
/exit       - Выход
```

## 🌐 REST API режим

### Запуск

```bash
python main.py --mode api
```

### API Endpoints

```bash
# Сообщение от пациента
curl -X POST "http://localhost:8000/message/patient" \
  -H "Content-Type: application/json" \
  -d '{"message": "У меня болит горло"}'

# Сообщение от врача
curl -X POST "http://localhost:8000/message/doctor" \
  -H "Content-Type: application/json" \
  -d '{"message": "Какие диагнозы?"}'

# Информация о сеансе
curl "http://localhost:8000/session"

# История разговора
curl "http://localhost:8000/session/history"

# Документация (откройте в браузере)
# http://localhost:8000/docs
```

## 🐳 Docker режим

### Запуск

```bash
docker-compose up
```

Приложение будет доступно на `http://localhost:8000`

## 🧪 Примеры

### Запустите все примеры

```bash
python examples.py
```

**Демонстрирует:**
- Базовое использование агента
- Сбор анамнеза через анкету
- RAG систему
- Полный рабочий процесс

## ⚙️ Конфигурация

### Основные параметры (.env)

```env
# Какую модель использовать
OLLAMA_MODEL=mistral         # или neural-chat, llama2

# Язык интерфейса
UI_LANGUAGE=uk              # uk, ru, en

# Режим по умолчанию
APP_MODE=cli                # cli, api

# Размер модели Whisper (для STT)
WHISPER_MODEL_SIZE=base     # tiny, base, small, medium, large
```

## 🎤 Голосовой режим

Требует:
- Микрофон
- Динамики
- Python зависимости (уже установлены)

```bash
# Включить голос
python main.py --mode cli --voice

# Или через конфиг
# Отредактируйте .env и используйте
```

## 🔍 Структура проекта

```
📦 MedicalAgent2
├── 📄 main.py                    ← Запуск отсюда
├── 📄 examples.py                ← Примеры
├── 📄 setup.py                   ← Инициализация
├── 📂 src/
│   ├── core/                     ← Основные компоненты
│   │   ├── agent.py              ← Главный агент
│   │   ├── llm_manager.py        ← Ollama интеграция
│   │   ├── memory.py             ← Память разговора
│   │   └── medical_logic.py      ← Медицинская логика
│   ├── voice/                    ← Голос
│   │   ├── speech_to_text.py     ← Whisper
│   │   └── text_to_speech.py     ← Piper
│   ├── medical/                  ← Медицина
│   │   ├── questionnaire.py      ← Анкета
│   │   └── rag.py                ← RAG система
│   └── ui/                       ← Интерфейсы
│       ├── cli.py                ← Командная строка
│       └── api.py                ← REST API
├── 📂 data/
│   └── medical_kb/               ← База знаний
└── 📄 requirements.txt            ← Зависимости
```

## 🆘 Решение проблем

### Ollama не подключается

```bash
# Проверьте что Ollama запущена в другом окне
ollama serve

# Проверьте моделЬ
ollama list

# Если модель не загружена
ollama pull mistral
```

### Нет звука

```bash
# Windows обычно работает из коробки
# macOS:
brew install portaudio
pip install --force-reinstall pyaudio

# Linux:
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Ошибка при запуске

```bash
# Проверьте Python версию (должна быть 3.10+)
python --version

# Переустановите зависимости
pip install --force-reinstall -r requirements.txt
```

## 📊 Производительность

| Компонент | Время |
|-----------|-------|
| Распознавание речи (STT) | 2-5 сек |
| LLM ответ | 1-3 сек |
| Синтез речи (TTS) | 1-2 сек |
| **Полный цикл** | **~5-10 сек** |

**Требования:**
- RAM: 8 GB минимум, 16 GB рекомендуется
- CPU: 4+ ядра
- Место: 20 GB для моделей

## 🎯 Следующие шаги

### Для тестирования
1. ✅ Запустите `python examples.py`
2. ✅ Попробуйте CLI режим: `python main.py --mode cli`
3. ✅ Проверьте API: `python main.py --mode api`

### Для интеграции
1. 🔗 Используйте REST API для интеграции в другие системы
2. 📦 Используйте Docker для развертывания
3. 🔧 Модифицируйте под ваши нужды

### Для расширения
1. 📚 Добавьте больше документов в `data/medical_kb/`
2. 🧠 Настройте prompt'ы в `llm_manager.py`
3. 💾 Интегрируйте свою базу знаний через RAG

## 📚 Полезные ссылки

- 🦙 [Ollama](https://ollama.ai) - Локальная LLM
- 🎤 [Whisper](https://github.com/openai/whisper) - STT
- 🔊 [Piper](https://github.com/rhasspy/piper) - TTS
- ⚡ [FastAPI](https://fastapi.tiangolo.com/) - API фреймворк
- 🧠 [LangChain](https://langchain.com/) - LLM управление

## 💡 Советы

1. **Начните с CLI** - Это проще для понимания
2. **Используйте примеры** - `python examples.py` показывает все возможности
3. **Читайте логи** - Запустите с `--debug` для отладки
4. **Попробуйте разные модели** - `mistral`, `neural-chat`, `llama2`
5. **Используйте Docker** - Для простого развертывания

## 🎉 Готово!

```bash
# Все готово! Просто запустите:
python main.py --mode cli

# Или для тестирования:
python examples.py
```

**Поздравляем! Ваш локальный медицинский ИИ-помощник готов к работе! 🚀**

---

### ❓ Вопросы?

1. Прочитайте [README.md](README.md) для полной документации
2. Смотрите [QUICKSTART.md](QUICKSTART.md) для примеров
3. Проверьте [INSTALLATION.md](INSTALLATION.md) для решения проблем
4. Изучите код в `src/` для понимания архитектуры

**Успехов в разработке! 💪**
