FROM python:3.11-slim

WORKDIR /app/worker

RUN pip install requests psycopg2-binary sqlalchemy kafka-python-ng && apt-get update && apt-get install -y kafkacat

CMD ["./wait-for-kafka.sh", "python", "worker.py"]
