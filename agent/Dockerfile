FROM python:3.11-slim

WORKDIR /app

RUN pip install requests kafka-python-ng && apt-get update && apt-get install -y kafkacat

CMD ["./wait-for-kafka.sh", "python", "agent.py"]
