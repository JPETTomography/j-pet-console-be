import socket


def start_socket_client(host='localhost', port=12345):
    # Create a socket to connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((host, port))
    print(f"Connected to server at {host}:{port}")

    # Send data to the server
    message = "Hello, Server!"
    client_socket.sendall(message.encode('utf-8'))

    # Receive a response from the server
    response = client_socket.recv(1024)
    print(f"Received from server: {response.decode('utf-8')}")

    # Close the connection
    client_socket.close()


if __name__ == "__main__":
    start_socket_client()
