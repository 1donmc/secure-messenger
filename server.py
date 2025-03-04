import socket
import threading
import os
import queue
from datetime import datetime
from database import verify_user, register_user
from config import HOST, PORT, MAX_USERS

clients = {}  # Stores connected clients
message_queue = queue.Queue()
lock = threading.Lock()  # To prevent race conditions in multi-threading


def handle_client(client_socket, username):
    """Handles receiving and broadcasting messages for a client."""
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break

            if message.startswith("FILE_TRANSFER:"):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                filename, filesize = message[len("FILE_TRANSFER:"):].split(":")
                filesize = int(filesize)

                # Notify other users
                for user, client in clients.items():
                    if user != username:
                        client.send(
                            f"[{timestamp}] {username} is sending file: {filename}".encode()
                        )

                # Notify sender
                client_socket.send(
                    f"[{timestamp}] Sending file: {filename}...".encode()
                )
                handle_file_transfer(
                    client_socket, filename, filesize, username)

            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                formatted_message = f"[{timestamp}] {username}: {message}"

                # Send message to other users, but NOT back to sender
                for user, client in clients.items():
                    if user != username:
                        client.send(formatted_message.encode())

    except:
        pass  # Handle disconnection silently
    finally:
        with lock:
            if username in clients:
                del clients[username]
        print(f"{username} has disconnected.")
        client_socket.close()


def handle_file_transfer(client_socket, filename, filesize, username):
    """Handles receiving a file from a client and saving it."""
    save_dir = "received_files"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    received_size = 0
    with open(save_path, "wb") as file:
        while received_size < filesize:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            file.write(chunk)
            received_size += len(chunk)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_socket.send(f"[{timestamp}] FILE_SENT: {filename}".encode())

    # Notify other users
    for user, client in clients.items():
        if user != username:
            client.send(f"[{timestamp}] FILE_RECEIVED: {filename}".encode())


def start_server():
    """Starts the chat server and handles incoming connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)  # Allow a few connections to queue up
    print(f"Server started on {HOST}:{PORT}...")

    while True:
        client_socket, addr = server.accept()

        with lock:
            if len(clients) >= MAX_USERS:
                print("Maximum users connected. Rejecting new connection.")
                client_socket.send("SERVER_FULL".encode())  # Notify client
                client_socket.close()  # Properly close the socket
                continue

        # Receive username and password
        credentials = client_socket.recv(1024).decode().split(":")
        if len(credentials) != 2:
            client_socket.close()
            continue

        username, password = credentials

        with lock:
            if username in clients:
                client_socket.send("USERNAME_TAKEN".encode())
                client_socket.close()
                continue

            if verify_user(username, password):
                client_socket.send("LOGIN_SUCCESS".encode())
                clients[username] = client_socket
                print(f"{username} connected from {addr}")

                threading.Thread(target=handle_client, args=(
                    client_socket, username)).start()
            else:
                client_socket.send("LOGIN_FAILED".encode())
                client_socket.close()


start_server()
