FROM python:3.11-slim

WORKDIR /app/

RUN apt-get update && apt-get install -y kafkacat && rm -rf /var/likb/apt/lists/*
RUN pip install fastapi uvicorn psycopg2-binary sqlalchemy kafka-python-ng faker sqladmin


# @TODO this is deplo option CMD ["./wait-for-kafka.sh", "./entrypoint_no_reload.sh"]
CMD ["./common/wait-for-kafka.sh", "./backend/entrypoint.sh"]
