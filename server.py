import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server listening on {HOST}:{PORT}")

clients = []  # List to store client connections

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    clients.append(conn)  # Add the connection to the clients list
    
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received from {addr}: {data.decode()}")

            # Broadcast the message to all clients
            for client in clients:
                if client != conn:  # Avoid sending the message back to the sender
                    client.sendall(data)
    except ConnectionResetError:
        pass  # Handle client disconnecting abruptly
    finally:
        # Remove the client from the list and close the connection
        clients.remove(conn)
        conn.close()
        print(f"Connection closed: {addr}")

try:
    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

except KeyboardInterrupt:
    print("\nServer shutting down...")
    # Close all client connections
    for client in clients:
        client.close()
    server_socket.close()
    print("Server stopped.")
