FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y kafkacat && rm -rf /var/likb/apt/lists/*
RUN pip install fastapi uvicorn psycopg2-binary sqlalchemy kafka-python-ng

# @TODO this is deplo option CMD ["./wait-for-kafka.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["./wait-for-kafka.sh", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
