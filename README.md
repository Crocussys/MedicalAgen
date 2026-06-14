# Медицинский ИИ-Помощник (Medical AI Assistant)

Локальный ИИ-агент для помощи врачам в диагностике пациентов с голосовым управлением.

## Возможности

- 🎙️ **Голосовой ввод/вывод**: Распознавание речи пациента и врача (Whisper) и синтез речи (TTS)
- 🧠 **Локальная LLM**: Работает полностью без интернета (Ollama)
- 📋 **Сбор анамнеза**: Автоматический сбор истории болезни пациента
- 🔍 **RAG система**: Поиск информации в медицинской базе знаний
- 💬 **Диалоговое управление**: Естественное общение с врачом и пациентом
- 🏥 **Помощь при диагностике**: Анализ симптомов и предложение возможных диагнозов

## Требования

- Python 3.10+
- Ollama (для локальной LLM)
- FFmpeg (для обработки аудио)
- 8GB+ RAM (рекомендуется 16GB+)

## Установка

### 1. Установите Ollama
Скачайте с [ollama.ai](https://ollama.ai)

### 2. Клонируйте репозиторий и установите зависимости
```bash
cd MedicalAgent2
pip install -r requirements.txt
```

### 3. Скачайте медицинскую базу знаний
```bash
python scripts/download_medical_kb.py
```

### 4. Запустите приложение
```bash
python main.py
```

## Архитектура

```
MedicalAgent2/
├── src/
│   ├── core/                 # Ядро агента
│   │   ├── agent.py          # Основной класс агента
│   │   ├── llm_manager.py    # Управление LLM (Ollama)
│   │   └── memory.py         # Память для контекста диалога
│   ├── voice/                # Голосовые компоненты
│   │   ├── speech_to_text.py # Whisper для распознавания
│   │   └── text_to_speech.py # TTS для синтеза
│   ├── rag/                  # RAG система
│   │   ├── embeddings.py     # Генерация эмбеддингов
│   │   ├── vector_store.py   # Хранилище векторов
│   │   └── retriever.py      # Поиск информации
│   ├── ui/                   # Интерфейс
│   │   ├── cli.py            # Командная строка
│   │   ├── api.py            # REST API (FastAPI)
│   │   └── web.py            # Веб-интерфейс
│   ├── medical/              # Медицинские компоненты
│   │   ├── questionnaire.py  # Анкета пациента
│   │   ├── anamnesis.py      # Сбор анамнеза
│   │   └── diagnosis.py      # Помощь при диагностике
│   └── config.py             # Конфигурация
├── data/
│   ├── medical_kb/           # Медицинская база знаний
│   ├── questionnaires/       # Шаблоны анкет
│   └── vectors/              # Сохраненные эмбеддинги
├── models/                   # Загруженные модели
├── scripts/
│   ├── download_medical_kb.py
│   ├── build_vectors.py
│   └── test_components.py
├── tests/
├── main.py                   # Точка входа
├── requirements.txt          # Зависимости
└── .env.example              # Пример конфигурации
```

## Использование

### Командная строка
```bash
python main.py --mode cli
```

### REST API
```bash
python main.py --mode api
```

### Веб-интерфейс
```bash
python main.py --mode web
```

## Модели

- **LLM**: Ollama (рекомендуется `mistral` или `neural-chat`)
- **Speech-to-Text**: OpenAI Whisper (локальная версия)
- **Text-to-Speech**: Piper или gTTS
- **Embeddings**: Ollama embeddings или ONNX модели

## Лицензия

MIT
