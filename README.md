# Secure Chat Messenger

A simple Python-based secure chat messenger that supports multiple users, authentication, and file transfer.

## Features

- User authentication (register/login)
- Real-time messaging
- File transfer
- Notification sound and system alerts
- Maximum of 3 connected users at a time

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/messenger.git
cd messenger
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Server Settings

Edit `config.py` (if needed):

```python
HOST = "0.0.0.0"
PORT = 5556
MAX_USERS = 3
```

### 4. Initialize the Database

Run:

```bash
python database.py
```

This will create `users.db` with a users table.

### 5. Start the Server

```bash
python server.py
```

### 6. Start the Client

Run the client on each user's machine:

```bash
python client.py
```

---

## File Structure

```
├── client.py         # Chat client with GUI
├── server.py         # Chat server with user authentication
├── database.py       # Handles user registration and verification
├── config.py         # Configurable host, port, and max users
├── received_files/   # Stores received files
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

---

## Code Overview

### `server.py` - The Chat Server

```python
import socket
import threading
import os
import queue
from datetime import datetime
from database import verify_user
from config import HOST, PORT, MAX_USERS

clients = {}

...

if len(clients) >= MAX_USERS:
    client_socket.send("SERVER_FULL".encode())
    client_socket.close()
    continue
```

### `client.py` - The Chat Client

```python
import socket
import threading
import tkinter as tk
from database import verify_user
...
self.client.send(f"{self.username}:{self.password}".encode())
response = self.client.recv(1024).decode()
if response == "SERVER_FULL":
    messagebox.showerror("Error", "Server is full! Try again later.")
    self.root.destroy()
    return
```

### `database.py` - Handles User Authentication

```python
import sqlite3
import bcrypt

DB_FILE = "users.db"
...
if row and bcrypt.checkpw(password.encode(), row[0]):
    return True
return False
```

### `config.py` - Configuration File

```python
HOST = "0.0.0.0"
PORT = 5556
MAX_USERS = 3
```

---

## Notes

- The server allows only **3 users** at a time.
- If the server is full, clients get a `SERVER_FULL` message and exit.
- File transfers are saved in `received_files/`.
- Notifications play a sound if not muted.

---

## Future Improvements

- End-to-end encryption for messages.
- Improve UI design for a better experience.
- Add support for more file types.

Enjoy chatting! 🚀
