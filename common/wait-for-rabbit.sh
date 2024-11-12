#!/bin/sh

echo "Waiting for RabbitMQ..."

# Check if nc (Netcat) is installed
if ! command -v nc >/dev/null 2>&1; then
    echo "Netcat (nc) is not installed."
    exit 1
fi

RABBITMQ_HOST="rabbitmq"  # Change this to your RabbitMQ host if needed
RABBITMQ_PORT="5672"       # RabbitMQ default port is 5672

# Loop until RabbitMQ is ready
while ! nc -z $RABBITMQ_HOST $RABBITMQ_PORT; do
    echo "RabbitMQ is not available yet. Retrying in 5 seconds..."
    sleep 5
done

echo "RabbitMQ started"

# Execute the provided command
exec "$@"
