# Архитектура Медицинского ИИ-Помощника

## 🏗️ Общая архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   CLI        │  │   REST API   │  │   WebSocket  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────┐
│               Medical AI Agent (Core)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Agent Logic                                        │   │
│  │  - Patient Interview                               │   │
│  │  - Doctor Assistance                               │   │
│  │  - Diagnosis Suggestions                           │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────┬──────────────┬──────────────┬────────────────────┘
           │              │              │
   ┌───────▼────┐ ┌───────▼────┐ ┌────▼──────────┐
   │             │ │            │ │               │
┌──▼────────┐  ┌─▼────────────┐ │ ┌──────────┐  │
│   Voice   │  │              │ │ │ Medical  │  │
│  I/O      │  │   LLM        │ │ │  Logic   │  │
├──────────┐│  │  Manager     │ │ └──────────┘  │
│ STT      ││  │ (Ollama)     │ │ ┌──────────┐  │
│ TTS      ││  │              │ │ │   RAG    │  │
└──────────┘│  └──────────────┘ │ │ System   │  │
            │                    │ └──────────┘  │
            │  ┌──────────────┐  │               │
            │  │   Memory     │  │               │
            │  │  Management  │  │               │
            │  └──────────────┘  │               │
            │                    │               │
            └────────────────────┴───────────────┘
                    │
        ┌───────────▼──────────┐
        │  External Services   │
        │  ├─ Ollama LLM       │
        │  ├─ Whisper STT      │
        │  └─ Piper TTS        │
        └──────────────────────┘
```

## 📦 Компоненты системы

### 1. **Voice Components** (`src/voice/`)
- **SpeechRecognizer**: Распознавание речи через Whisper
- **TextToSpeech**: Синтез речи через Piper

### 2. **Core Components** (`src/core/`)
- **MedicalAgent**: Основной класс агента
- **LLMManager**: Управление локальной LLM через Ollama
- **ConversationMemory**: Управление памятью разговора
- **MedicalLogic**: Медицинская логика и помощь в диагностике

### 3. **Medical Components** (`src/medical/`)
- **Questionnaire**: Анкета для сбора информации о пациенте
- **RAGSystem**: Система поиска в медицинской базе знаний

### 4. **User Interfaces** (`src/ui/`)
- **CLIInterface**: Интерфейс командной строки
- **APIServer**: REST API с FastAPI

## 🔄 Рабочий процесс

### Сценарий 1: Сбор анамнеза

```
1. Пациент -> "У меня болит горло"
                    ↓
2. Agent.process_patient_message()
                    ↓
3. LLMManager.extract_medical_info()
                    ↓
4. ConversationMemory.add_patient_message()
                    ↓
5. MedicalLogic.update_symptoms()
                    ↓
6. LLMManager.generate_response() -> Следующий вопрос
                    ↓
7. TextToSpeech.speak() -> Агент озвучивает вопрос
```

### Сценарий 2: Помощь врачу

```
1. Врач -> "/suggest_diagnosis"
                    ↓
2. Agent.process_doctor_command()
                    ↓
3. MedicalLogic.suggest_diagnosis()
                    ↓
4. RAGSystem.augment_context() -> Поиск в БЗ
                    ↓
5. LLMManager.generate_response() -> Предложения диагнозов
                    ↓
6. Вывод результатов врачу
```

## 💾 Структура данных

### Session
```python
{
    "id": "2024-01-15T10:30:00",
    "patient_info": {
        "age": 35,
        "gender": "male",
        "allergies": "пенициллин"
    },
    "symptoms": ["кашель", "температура", "боль в горле"],
    "conversation": [...]
}
```

### Message
```python
{
    "role": "patient|doctor|agent",
    "content": "текст сообщения",
    "timestamp": "2024-01-15T10:30:15"
}
```

## 🧠 LLM Integration

### Ollama
```
┌──────────────┐
│   Ollama     │  Port: 11434
│   LLM        │  Models: mistral, neural-chat, llama2
│   Server     │
└──────────────┘
     ↑
     │ HTTP API
     │
┌────▼──────────────┐
│ LLMManager         │
│ - generate_response│
│ - extract_info     │
│ - extract_command  │
└────────────────────┘
```

### Prompts
- **System Prompt**: Определяет роль агента (медицинский помощник)
- **Task Prompts**: Специфичные для каждой задачи (ask_question, summarize, etc.)

## 🔍 RAG System

```
Query: "У пациента симптомы X, Y, Z"
  ↓
Query Embedding / Text Search
  ↓
Knowledge Base Search
  ↓
Top-K Documents Retrieved (K=3)
  ↓
Augmented Context = Base Context + Retrieved Docs
  ↓
LLM Generate Response with Augmented Context
```

## 🗄️ Knowledge Base

```json
{
  "documents": [
    {
      "id": "disease-001",
      "title": "ОРВИ - симптомы и лечение",
      "content": "...",
      "category": "diseases",
      "metadata": {...}
    },
    ...
  ]
}
```

## 🔐 Security Considerations

1. **Local Processing**: Все обрабатывается локально, без отправки данных
2. **No API Keys**: Не требуются облачные сервисы
3. **Data Privacy**: Чувствительная медицинская информация остается в системе
4. **User Control**: Полный контроль над данными

## ⚡ Performance

- **Memory Usage**: ~2-4GB (LLM + Whisper + все компоненты)
- **CPU/GPU**: Может работать на CPU, но медленнее
- **Response Time**: 
  - STT: 2-5 сек на 10 сек аудио
  - LLM: 1-3 сек (зависит от модели)
  - TTS: ~1-2 сек на 100 слов

## 🔧 Расширяемость

### Добавление новой модели LLM
1. Загрузите модель в Ollama
2. Измените `OLLAMA_MODEL` в `.env`

### Добавление нового языка
1. Добавьте переводы в компоненты
2. Установите `UI_LANGUAGE` в `.env`

### Добавление новых симптомов/болезней
1. Отредактируйте `src/core/medical_logic.py`
2. Добавьте документы в `data/medical_kb/`

## 📊 Мониторинг

### Логи
```
logs/
├── 2024-01-15.log
├── errors.log
└── debug.log
```

### Метрики
- Количество вопросов за сеанс
- Среднее время ответа
- Точность распознавания речи

---

**Архитектура разработана для модульности, масштабируемости и локального запуска!**
