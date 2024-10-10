#!/bin/sh

echo "Waiting for kafka..."

while ! kcat -b kafka:9092 -L; do
    sleep 5
done

echo "Kafka started"

exec "$@"
