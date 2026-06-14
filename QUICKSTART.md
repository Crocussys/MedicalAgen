# Быстрый старт - Medical AI Assistant

## 🚀 Установка за 5 минут

### Шаг 1: Установите зависимости

```bash
# Клонируйте репозиторий (если еще не сделали)
git clone <repository_url>
cd MedicalAgent2

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 2: Установите Ollama

Скачайте и установите Ollama с [ollama.ai](https://ollama.ai)

```bash
# Запустите Ollama
ollama serve

# В другом терминале - загрузите модель
ollama pull mistral
# или
ollama pull neural-chat
```

### Шаг 3: Запустите приложение

```bash
# Режим командной строки
python main.py --mode cli

# Режим командной строки с голосом
python main.py --mode cli --voice

# REST API режим
python main.py --mode api

# С голосом
python main.py --mode api --voice --debug
```

## 📚 Примеры использования

### Пример 1: Простой диалог

```bash
python main.py --mode cli
```

В интерфейсе:
```
👤 Пациент> У меня болит горло
🤖 Агент: Как долго у вас болит горло? Есть ли повышенная температура?
```

### Пример 2: Запуск примеров кода

```bash
python examples.py
```

Это демонстрирует:
- Базовое использование агента
- Сбор анамнеза через анкету
- RAG систему
- Полный рабочий процесс

### Пример 3: REST API

```bash
# Запуск API сервера
python main.py --mode api

# В другом терминале или в Postman:
curl -X POST "http://localhost:8000/message/patient" \
  -H "Content-Type: application/json" \
  -d '{"message": "У меня болит горло"}'
```

## 🎙️ Голосовой режим

Для голосового режима нужны:
- Микрофон
- Динамики
- PyAudio: `pip install pyaudio`

```bash
python main.py --mode cli --voice
```

## 🐳 Docker запуск

```bash
# Запустите все сервисы
docker-compose up

# Приложение будет доступно на http://localhost:8000
```

## ⚙️ Конфигурация

Отредактируйте `.env`:

```env
# Модель LLM
OLLAMA_MODEL=mistral

# Язык интерфейса
UI_LANGUAGE=uk

# Режим работы
APP_MODE=cli
```

## 🧪 Тестирование

```bash
# Запустите примеры
python examples.py

# Проверьте компоненты
python scripts/test_components.py
```

## 🔗 API Endpoints (для режима API)

- `GET /health` - Проверка здоровья
- `POST /message/patient` - Сообщение от пациента
- `POST /message/doctor` - Сообщение от врача
- `GET /session` - Информация о текущей сессии
- `POST /session/reset` - Сброс сессии
- `GET /session/history` - История разговора
- `WS /ws/chat` - WebSocket для реального времени

## 📋 Доступные команды в CLI

- `/help` - Справка
- `/patient` - Режим пациента
- `/doctor` - Режим врача
- `/voice` - Переключить голос
- `/status` - Статус сеанса
- `/clear` - Очистить память
- `/exit` - Выход

## 🆘 Решение проблем

### Ollama не подключается
```bash
# Проверьте, что Ollama запущена
ollama serve

# Проверьте, что модель загружена
ollama list
```

### Нет звука
```bash
# Установите PyAudio (может требовать зависимостей)
pip install pyaudio

# На Linux:
sudo apt-get install portaudio19-dev python3-pyaudio

# На macOS:
brew install portaudio
pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio
```

### ошибка модели
```bash
# Перезагрузите модель
ollama rm mistral
ollama pull mistral
```

## 📖 Документация

- [README.md](README.md) - Полная документация
- [examples.py](examples.py) - Примеры кода
- [ARCHITECTURE.md](ARCHITECTURE.md) - Архитектура системы

## 🤝 Поддержка

Для вопросов и ошибок создавайте Issues в репозитории.

## 📝 Лицензия

MIT

---

**Готово! Ваша медицинская ИИ система готова к работе! 🎉**
