import socket
import json
import argparse
import pika


def receive_data(producer_info):

    producer_ip = producer_info['ip']
    producer_port = producer_info['port']

    # Connect to the producer’s socket server to receive JSON data
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((producer_ip, producer_port))
        print(f"Connected to producer at {producer_ip}:{producer_port}")

        buffer = ""
        # Receive JSON data
        while True:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                break
            buffer += data
        json_data = json.loads(buffer)
        print("Received JSON data:", json.dumps(json_data, indent=2))


TOPIC = "root_json"

rabbitmq_host = "rabbitmq"
credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters(
    rabbitmq_host,  # replace with RabbitMQ server IP if not local
    5672,         # default RabbitMQ port
    '/',
    credentials
)


def consume_messages():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare the queue (make sure it exists)
    channel.queue_declare(queue='worker_topic', durable=True)
    # Set up consumer
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='worker_topic', on_message_callback=callback)

    print("Waiting for messages...")
    channel.start_consuming()

def callback(ch, method, properties, body):
    producer_info = json.loads(body.decode())
    print(f"Received producer IP and port info: {producer_info}")
    receive_data(producer_info)




if __name__ == "__main__":
    consume_messages()

