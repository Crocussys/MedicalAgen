# Требования к установке

## 📋 Системные требования

### Минимальные
- CPU: 4-ядерный процессор
- RAM: 8 GB
- SSD: 20 GB (для моделей и данных)
- OS: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

### Рекомендуемые  
- CPU: 8+ ядер
- RAM: 16 GB
- GPU: NVIDIA (CUDA) или Apple Silicon
- SSD: 50 GB

## 🐍 Python

- **Python 3.10** или выше
- pip (менеджер пакетов Python)

Проверка:
```bash
python --version
pip --version
```

## 📦 Основные зависимости

### Языковые модели
- **Ollama** 0.1+ - Для локальной LLM
- **Whisper** 20231117+ - Распознавание речи

### Зависимости Python
Все содержатся в `requirements.txt`:
```
ollama>=0.1
langchain>=0.1
openai-whisper>=20231117
piper-tts>=1.2.0
fastapi>=0.109.0
librosa>=0.10.0
sounddevice>=0.4.6
faiss-cpu>=1.7.4
sentence-transformers>=2.2.2
```

## 🔊 Аудио компоненты

Для голосового режима нужны:

### Windows
1. **Микрофон и динамики** (встроенные или USB)
2. **PyAudio** (автоматически установится из requirements.txt)

### macOS
```bash
brew install portaudio
pip install pyaudio
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

## 🦙 Ollama

### Установка
1. Скачайте с [ollama.ai](https://ollama.ai)
2. Запустите установщик
3. Откройте терминал и проверьте:
```bash
ollama --version
```

### Загрузка моделей

**Рекомендуемые модели:**

```bash
# Mistral - хороший баланс скорость/качество
ollama pull mistral

# Neural Chat - оптимизирован для диалога
ollama pull neural-chat

# Llama 2 - большая и мощная
ollama pull llama2

# Tiny - для слабых компьютеров
ollama pull tinyllama
```

Проверка загруженных моделей:
```bash
ollama list
```

## 🎤 Whisper

Автоматически загружается при первом запуске:

```python
import whisper
model = whisper.load_model("base")  # tiny, base, small, medium, large
```

**Размеры моделей:**
- tiny: 39M
- base: 140M
- small: 483M
- medium: 1.5G
- large: 2.9G

## 📥 Установка проекта

### 1. Клонирование репозитория
```bash
git clone <repository_url>
cd MedicalAgent2
```

### 2. Создание виртуального окружения
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка окружения
```bash
# Копируем пример конфигурации
cp .env.example .env

# Отредактируйте .env если нужно
# nano .env
```

### 5. Инициализация
```bash
python setup.py
```

## 🐳 Docker установка

### Требования
- Docker 20.10+
- Docker Compose 1.29+

### Запуск
```bash
docker-compose up
```

Приложение будет доступно на `http://localhost:8000`

## ✅ Проверка установки

```bash
# Проверка Python пакетов
python -c "import ollama; import whisper; print('✓ OK')"

# Проверка Ollama
ollama serve

# Запуск примеров
python examples.py

# Запуск основного приложения
python main.py --mode cli
```

## 🆘 Решение проблем

### ImportError: No module named 'pyaudio'
```bash
# Установите portaudio dev файлы сначала
# Windows: использует binaries автоматически
# macOS: brew install portaudio
# Linux: sudo apt-get install portaudio19-dev
pip install --force-reinstall pyaudio
```

### OSError: [Errno 2] No such file or directory: 'ollama'
```bash
# Убедитесь что Ollama установлена и в PATH
which ollama  # macOS/Linux
where ollama  # Windows

# Или запустите Ollama перед приложением
ollama serve &
```

### RuntimeError: No CUDA devices available
```bash
# Это нормально для CPU-only режима
# Приложение работает на CPU, но медленнее
# Для CUDA установите torch с CUDA поддержкой (опционально)
```

### ModuleNotFoundError: No module named 'requirements'
```bash
# Убедитесь что вы установили зависимости
pip install -r requirements.txt
```

## 📝 Переменные окружения (.env)

```env
# Ollama LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_TIMEOUT=300

# Whisper (для STT)
WHISPER_MODEL_SIZE=base
DEVICE=cpu

# TTS
TTS_ENGINE=piper
TTS_VOICE=uk_UA-mykyta-x_low
TTS_SPEED=1.0

# Приложение
APP_MODE=cli
APP_DEBUG=false
APP_HOST=0.0.0.0
APP_PORT=8000

# Языки
UI_LANGUAGE=uk
MODEL_LANGUAGE=en
```

## 📊 Проверка ресурсов

```bash
# Проверьте использование памяти
# Windows: Диспетчер задач
# macOS: Activity Monitor
# Linux: top, htop

# Рекомендуемо минимум 1.5GB свободной памяти
```

---

**Готово! Ваша система установлена и готова к работе! ✅**
