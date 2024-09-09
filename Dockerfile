# Этап 1: Сборочный этап
FROM python:3.12 AS builder

# Создаем рабочую директорию /src для исходного кода и /venv для виртуального окружения
WORKDIR /src/

# Копируем только необходимые файлы для установки зависимостей
COPY pyproject.toml ./

# Устанавливаем PDM и создаем виртуальное окружение вручную в /venv
RUN pip install pdm \
    && python -m venv /venv \
    && . /venv/bin/activate \
    && pdm install --production

# Этап 2: Финальный этап
FROM python:3.12

# Рабочая директория для приложения /src
WORKDIR /src/

# Копируем установленное виртуальное окружение с первого этапа в /venv
COPY --from=builder /venv /venv

# Копируем остальные файлы приложения в /src
COPY . .

# Устанавливаем переменные окружения для активации виртуального окружения и добавляем PYTHONPATH
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH="/src"

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y tree

# Выводим структуру директорий для отладки
RUN tree

# Проверяем, что файл alembic.ini существует
RUN ls -l /src/alembic.ini

# Устанавливаем Alembic для управления миграциями
RUN pip install alembic

# Применяем миграции Alembic
RUN alembic upgrade head

# Открываем необходимый порт
EXPOSE 80

# Запускаем приложение через Uvicorn
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]
