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
# RUN apt-get update && apt-get install -y postgresql-client

# Check that the alembic.ini file exists
# RUN ls -la

# Copy the wait script into the container
# COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
# RUN chmod +x /usr/local/bin/wait-for-it.sh

# Expose the necessary port
EXPOSE 80

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 80"]