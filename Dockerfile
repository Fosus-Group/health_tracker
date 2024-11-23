# Этап 1: Сборочный этап
FROM python:3.12.4-alpine AS builder

WORKDIR /src/

# Установка инструментов сборки для Alpine
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev

# Копирование файлов pyproject.toml и pdm.lock
COPY pyproject.toml pdm.lock ./

# Установка переменной окружения для создания виртуального окружения
ENV PDM_VENV_IN_PROJECT=1

# Установка PDM и зависимостей
RUN pip install --upgrade pip && \
    pip install --no-cache-dir pdm && \
    PDM_IGNORE_ACTIVE_VENV=1 pdm install --production -v && \
    ls -al /src/.venv

# Очистка кэша PDM
RUN rm -rf ~/.cache/pdm

# Этап 2: Финальный образ
FROM python:3.12.4-alpine

WORKDIR /src

# Установка PostgreSQL клиента
RUN apk add --no-cache libpq

# Копирование виртуального окружения из сборочного этапа
COPY --from=builder /src/.venv /venv

# Копирование остального кода приложения
COPY . .

# Настройка окружения
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH="/src"

# Переменные для подключения к базе данных
ARG PG_HOST=rc1b-nj3ubmon8dl2it6r.mdb.yandexcloud.net
ARG PG_PORT=6432
ARG PG_DATABASE=health_tracker
ARG PG_USERNAME=health_tracker_db
ARG PG_PASSWORD=example

ENV PG_HOST=${PG_HOST}
ENV PG_PORT=${PG_PORT}
ENV PG_DATABASE=${PG_DATABASE}
ENV PG_USERNAME=${PG_USERNAME}
ENV PG_PASSWORD=${PG_PASSWORD}

# Открытие порта
EXPOSE 80

# Создание скрипта запуска
RUN echo '#!/bin/sh' > /src/start.sh && \
    echo 'alembic upgrade head' >> /src/start.sh && \
    echo 'uvicorn main:app --host 0.0.0.0 --port 80' >> /src/start.sh && \
    chmod +x /src/start.sh

# Указание команды запуска
CMD ["/bin/sh", "/src/start.sh"]
