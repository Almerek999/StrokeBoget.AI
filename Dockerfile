FROM python:3.10

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем системные пакеты (нужны для аудио и работы с камерой)
RUN apt-get update && apt-get install -y ffmpeg libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# Устанавливаем питон-библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# В Hugging Face Spaces по умолчанию используется порт 7860
ENV PORT=7860
EXPOSE 7860

# Запускаем сервер
CMD ["gunicorn", "src.app:app", "--bind", "0.0.0.0:7860", "--timeout", "120"]
