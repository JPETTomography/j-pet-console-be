from agent.histo2json import root_file_to_json
import logging
import socket
import json
import pika
import yaml
import time
import uuid
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# HOSTNAME = 'localhost'
HOST = "agent"
PORT = 12345
TOPIC = "root_json"


rabbitmq_host = "rabbitmq"
credentials = pika.PlainCredentials("user", "password")
parameters = pika.ConnectionParameters(
    rabbitmq_host,  # replace with RabbitMQ server IP if not local
    5672,  # default RabbitMQ port
    "/",
    credentials,
)


def send_message(topic, message):
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare a queue
    channel.queue_declare(queue="task_queue", durable=True)

    # Publish a message
    channel.basic_publish(
        exchange="",
        routing_key="worker_topic",
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        ),
    )

    print(f"Sent: {message}")
    connection.close()


# def consume_messages():
#     connection = pika.BlockingConnection(parameters)
#     channel = connection.channel()

#     channel.queue_declare(queue='agent_topic', durable=True)
#     channel.basic_qos(prefetch_count=1)
#     channel.basic_consume(queue='agent_topic', on_message_callback=callback)

#     print("Waiting for messages...")
#     channel.start_consuming()


def send_data(json_data, socket):
    connection_info = {"ip": HOST, "port": PORT, "uuid": str(uuid.uuid4())}
    encoded_info = json.dumps(connection_info).encode("utf-8")
    print("Sending connection info to Rabbit...")
    send_message("worker_topic", encoded_info)
    while True:
        connection, client_address = socket.accept()
        try:
            print(f"Connection established with {client_address}")
            encoded_data = json.dumps(json_data).encode("utf-8")
            connection.sendall(encoded_data)
        finally:
            connection.close()
            break
            print(f"Connection with {client_address} closed.")


def process_file(root_file_path, hist_def, socket):
    # hist_def = "examplary_data/histo_description.json"
    # root_file_path = "examplary_data/2024_02_14_14_57_dabc_24043183007.root"
    print("reading_data")
    root_json_data = root_file_to_json(hist_def, root_file_path)
    send_data(root_json_data, socket)


def read_config(filepath):
    with open(filepath) as f:
        config = yaml.safe_load(f)
    return config


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, hist_def):
        self.hist_def = hist_def
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(5)
        print(f"Server listening on {HOST}:{PORT}...")
        logging.info(f"Server listening on {HOST}:{PORT}...")

    def on_created(self, event):
        print("TRIGGERED!")
        try:
            if not event.is_directory:
                time.sleep(1)
                print(f"New file detected: {event.src_path}")
                process_file(
                    root_file_path=event.src_path,
                    hist_def=self.hist_def,
                    socket=self.server_socket,
                )
                print("FINISHED!")
        except Exception as e:
            print(f"Error processing file {event.src_path}: {e}")
        print("exiting on_created")



if __name__ == "__main__":
    # consume_messages()
    config = read_config("./agent/examplary_config.yaml")
    hist_def = config['detector']['hist_def']
    event_handler = NewFileHandler(hist_def=hist_def)
    observer = Observer()
    path_to_watch = config["detector"]['path_to_watch']
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
    observer.schedule(event_handler, path=path_to_watch, recursive=False)
    from watchdog.events import LoggingEventHandler
    # observer.schedule(LoggingEventHandler(), path=path_to_watch, recursive=False)
    observer.start()
    print(f"Watching folder: {path_to_watch}")

    try:
        while True:
            if not observer.is_alive():
                logging.error("Observer has stopped. Exiting...")
                break
            print("Agent is running...", time.ctime())
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
