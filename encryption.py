from cryptography.fernet import Fernet

SECRET_KEY = b'BttqQjQJmZlwE9uGjL-JhAULKLUsJruevTYsjxTSIEw='

cipher = Fernet(SECRET_KEY)


def encrypt_message(message: str) -> bytes:
    """Encrypts a message using AES."""
    return cipher.encrypt(message.encode())


def decrypt_message(encrypted_message: bytes) -> str:
    """Decrypts an encrypted message."""
    return cipher.decrypt(encrypted_message).decode()