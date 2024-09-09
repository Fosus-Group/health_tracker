# Stage 1: Builder stage
FROM python:3.12 AS builder

WORKDIR /app/

# Copy the pyproject.toml
COPY pyproject.toml ./

# Install PDM and create a virtual environment manually
RUN pip install pdm \
    && python -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pdm install 
    
# Stage 2: Final stage
FROM python:3.12

WORKDIR /app/

# Copy the installed virtual environment from the builder stage
COPY --from=builder /app/venv /app/venv

# Copy the rest of the application files
COPY . .

# Verify that alembic.ini exists
RUN ls -l app/alembic.ini

# Install Alembic
RUN pip install alembic

# Set environment variables to activate the virtual environment and add PYTHONPATH
ENV VIRTUAL_ENV=/app/venv
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Apply Alembic migrations
RUN alembic -c app/alembic.ini upgrade head

# Expose port and run the application
EXPOSE 80
ENTRYPOINT ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]
