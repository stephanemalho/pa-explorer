from cryptography.fernet import Fernet

from app.config import settings


def encrypt(plaintext: str) -> str:
    f = Fernet(settings.pa_explorer_encryption_key.encode())
    return f.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    f = Fernet(settings.pa_explorer_encryption_key.encode())
    return f.decrypt(ciphertext.encode()).decode()
