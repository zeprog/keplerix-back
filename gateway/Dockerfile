# Используем образ Python 3.12 как базовый
FROM python:3.12.1-slim-bullseye

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем рабочую директорию
WORKDIR /app

# Устанавливаем необходимые пакеты
RUN apt update -y && \
    apt install -y gcc

# Копируем файл зависимостей
COPY pyproject.toml /app/

# Устанавливаем pip и poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Настраиваем poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

# Копируем проект
COPY ./gateway /app/

# Указываем команду для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]