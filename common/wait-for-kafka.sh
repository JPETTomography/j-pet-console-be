#!/bin/sh

echo "Waiting for Kafka..."

# Check if kcat is installed, else fall back to kafkacat
if command -v kcat >/dev/null 2>&1; then
    KAFKA_CMD="kcat"
elif command -v kafkacat >/dev/null 2>&1; then
    KAFKA_CMD="kafkacat"
else
    echo "Neither kcat nor kafkacat is installed."
    exit 1
fi

# Loop until Kafka is ready
while ! $KAFKA_CMD -b kafka:9092 -L; do
    sleep 5
done

echo "Kafka started"

# Execute the provided command
exec "$@"
