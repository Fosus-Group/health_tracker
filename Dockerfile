FROM python:3.12

WORKDIR /app/
COPY . .
RUN pip install pdm
RUN pdm sync

WORKDIR /app/app/

EXPOSE 80

ENTRYPOINT ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]