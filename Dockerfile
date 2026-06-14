# Dockerfile для контейнеризации приложения

FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    ffmpeg \
    portaudio19-dev \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# Обновление pip и setuptools перед установкой зависимостей
RUN python -m pip install --upgrade pip setuptools wheel

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директорий для данных
RUN mkdir -p data/medical_kb data/vectors logs models

# Здоровье проверка
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Запуск приложения
CMD ["python", "main.py", "--mode", "api"]
