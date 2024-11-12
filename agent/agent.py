from agent.histo2json import root_file_to_json
import logging
import socket
import json
import pika
# HOSTNAME = 'localhost'
HOST = 'agent'
PORT = 12345
TOPIC = "root_json"


rabbitmq_host = "rabbitmq"
credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters(
    rabbitmq_host,  # replace with RabbitMQ server IP if not local
    5672,         # default RabbitMQ port
    '/',
    credentials
)


def send_message(topic, message):
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare a queue
    channel.queue_declare(queue='task_queue', durable=True)

    # Publish a message
    channel.basic_publish(
        exchange='',
        routing_key='worker_topic',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        ))

    print(f"Sent: {message}")
    connection.close()


def consume_messages():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare the queue (make sure it exists)
    channel.queue_declare(queue='agent_topic', durable=True)
    # Set up consumer
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='agent_topic', on_message_callback=callback)

    print("Waiting for messages...")
    channel.start_consuming()


def send_data(json_data, host=HOST, port=PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}...")
    logging.info(f"Server listening on {host}:{port}...")
    with open("server_info.json", "w") as f:
        f.write(f"Server listening on {host}:{port}...")

    connection_info = {"ip": HOST, "port": PORT}
    encoded_info = json.dumps(connection_info).encode('utf-8')
    print("Sending connection info to Kafka...")
    send_message("worker_topic", encoded_info)
    while True:
        connection, client_address = server_socket.accept()
        try:
            print(f"Connection established with {client_address}")
            encoded_data = json.dumps(json_data).encode('utf-8')
            connection.sendall(encoded_data)
        finally:
            connection.close()
            print(f"Connection with {client_address} closed.")


def callback(ch, method, properties, body):
    print(f"Received: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    hist_def = "examplary_data/histo_description.json"
    root_file_path = "examplary_data/2024_02_14_14_57_dabc_24043183007.root"
    print("reading_data")
    root_json_data = root_file_to_json(hist_def, root_file_path)

    task_info = json.loads(body.decode())
    match task_info["task"]:
        case "add_random_test_data":
            print("data read finished")
            send_data(root_json_data)
        case _:
            raise ValueError(f"Unknown task: {task_info['task']}")


if __name__ == "__main__":
    consume_messages()
