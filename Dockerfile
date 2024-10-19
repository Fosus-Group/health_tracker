# Этап 1: Сборочный этап
FROM python:3.12 AS builder

# Create a working directory /src for the source code and /venv for the virtual environment
WORKDIR /src/

# Copy only the necessary files for installing dependencies
COPY pyproject.toml ./

# Install PDM and manually create a virtual environment in /venv
RUN pip install pdm \
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
RUN apt-get update && apt-get install -y postgresql-client

# Добавляем переменные окружения для подключения к базе данных
ENV PG_HOST=${PG_HOST:-localhost}
ENV PG_PORT=${PG_PORT:-5432}
ENV PG_DATABASE=${PG_DATABASE:-health_tracker}
ENV PG_USERNAME=${PG_USERNAME:-postgres}
ENV PG_PASSWORD=${PG_PASSWORD:-example}

EXPOSE 80

# Создаем скрипт для запуска
RUN echo '#!/bin/sh' > /src/start.sh && \
    echo 'alembic upgrade head' >> /src/start.sh && \
    echo 'uvicorn main:app --host 0.0.0.0 --port 80' >> /src/start.sh && \
    chmod +x /src/start.sh

CMD ["/src/start.sh"]
