import socket
import json
from kafka import KafkaProducer, KafkaConsumer
import logging
from agent.histo2json import root_file_to_json
# HOSTNAME = 'localhost'
HOST = 'kafka_agent'
PORT = 12345
TOPIC = "root_json"

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
)

consumer = KafkaConsumer(
    "agent_topic",
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='worker-group'
)

def send_data(json_data,host=HOST, port=PORT):
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
    producer.send(TOPIC, encoded_info)
    while True:
        connection, client_address = server_socket.accept()
        try:
            print(f"Connection established with {client_address}")
            encoded_data = json.dumps(json_data).encode('utf-8')
            connection.sendall(encoded_data)
        finally:
            connection.close()
            print(f"Connection with {client_address} closed.")


if __name__ == "__main__":
    hist_def = "examplary_data/histo_description.json"
    root_file_path = "examplary_data/2024_02_14_14_57_dabc_24043183007.root"
    print("reading_data")
    root_json_data = root_file_to_json(hist_def, root_file_path)
    print("Waiting for messages...")
    try:
        for message in consumer:
            task_info = json.loads(message.value.decode('utf-8'))
            match task_info["task"]:
                case "add_random_test_data":
                    print("data read finished")
                    send_data(root_json_data)
                case _:
                    raise ValueError(f"Unknown task: {task_info['task']}")

    finally:
        # Ensure all uncommitted messages are committed before exiting
        print("Committing offsets and closing consumer...")
        consumer.commit()
        consumer.close()
        print("Consumer closed")
