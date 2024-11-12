import socket


def start_socket_server(host='0.0.0.0', port=12345):
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the address and port
    server_socket.bind((host, port))

   # Listen for incoming connections (maximum of 5 in the queue)
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}...")

    while True:
        # Wait for a connection
        connection, client_address = server_socket.accept()
        try:
            print(f"Connection established with {client_address}")

            # Receive the data sent by the client
            data = connection.recv(1024)
            if data:
                print(f"Received: {data.decode('utf-8')}")
                # Send a response back to the client
                response = "Data received successfully"
                connection.sendall(response.encode('utf-8'))
            else:
                print("No data received.")
        finally:
            # Clean up the connection
            connection.close()
            print(f"Connection with {client_address} closed.")


if __name__ == "__main__":
    start_socket_server()
