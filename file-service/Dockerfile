# Используем официальный Python образ
FROM python:3.12.1-slim-bullseye

# Отключаем кеширование байт-кода Python и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Обновляем apt и устанавливаем необходимые зависимости
RUN apt update -y && \
    apt install -y python3-dev gcc musl-dev

# Добавляем файл зависимостей
COPY pyproject.toml /app/
COPY poetry.lock /app/

# Обновляем pip и устанавливаем poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Настраиваем poetry для работы без виртуальных окружений и устанавливаем зависимости
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

# Копируем скрипт ожидания сервисов
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Копируем файлы приложения
COPY ./file-service /app/
COPY ./migrations /app/migrations

# Устанавливаем рабочую директорию
WORKDIR /app

# Выполняем миграции при запуске контейнера
CMD ["alembic", "upgrade", "head"]