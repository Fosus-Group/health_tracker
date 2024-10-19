# Этап 1: Сборочный этап
FROM python:3.12 AS builder

# Create a working directory /src for the source code and /venv for the virtual environment
WORKDIR /src/

# Copy only the necessary files for installing dependencies
COPY pyproject.toml ./

# Install PDM and manually create a virtual environment in /venv
RUN pip install --no-cache-dir pdm \
    && python -m venv /venv \
    && . /venv/bin/activate \
    && pdm install --production

# Stage 2: Final Stage
FROM python:3.12

# Working directory for the application /src
WORKDIR /src/

# Copy the installed virtual environment from the first stage into /venv
COPY --from=builder /venv /venv

# Copy the rest of the application files into /src
COPY . .

# Set environment variables to activate the virtual environment and add PYTHONPATH
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH="/src"

WORKDIR /src/app

# Install PostgreSQL client tools (to get pg_isready)
RUN apt-get update && apt-get install -y postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Добавляем переменные окружения для подключения к базе данных
ENV PG_HOST=${PG_HOST:-rc1b-nj3ubmon8dl2it6r.mdb.yandexcloud.net}
ENV PG_PORT=${PG_PORT:-6432}
ENV PG_DATABASE=${PG_DATABASE:-health_tracker}
ENV PG_USERNAME=${PG_USERNAME:-health_tracker_db}
ENV PG_PASSWORD=${PG_PASSWORD:-example}

EXPOSE 80

# Создаем нового пользователя и выполняем команды от его имени
RUN useradd -m appuser

# Создаем скрипт для запуска
RUN echo '#!/bin/sh' > /src/start.sh && \
    echo 'alembic upgrade head' >> /src/start.sh && \
    echo 'uvicorn main:app --host 0.0.0.0 --port 80' >> /src/start.sh && \
    chmod +x /src/start.sh

CMD ["/bin/sh", "/src/start.sh"]
