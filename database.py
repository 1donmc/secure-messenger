import sqlite3
import bcrypt

DB_FILE = "users.db"

# Initialize the database


def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Register a new user


def register_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Hash the password before storing
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True  # Registration successful
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

# Verify login credentials


def verify_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    conn.close()

    if row and bcrypt.checkpw(password.encode(), row[0]):
        return True  # Login successful
    return False  # Invalid credentials


# Run once to initialize the database
initialize_db()