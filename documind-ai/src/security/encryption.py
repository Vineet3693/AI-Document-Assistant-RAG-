"""Encryption module for document security"""

from cryptography.fernet import Fernet
from typing import Optional
import base64, os

class EncryptionManager:
    def __init__(self, key: Optional[str] = None):
        self.key = key or os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key().decode()
        self.cipher = Fernet(self.key.encode())
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()

def encrypt_file(file_path: str, output_path: str):
    with open(file_path, 'rb') as f:
        data = f.read()
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(data)
    with open(output_path, 'wb') as f:
        f.write(encrypted)
    return key.decode()

def decrypt_file(file_path: str, key: str, output_path: str):
    cipher = Fernet(key.encode())
    with open(file_path, 'rb') as f:
        data = f.read()
    decrypted = cipher.decrypt(data)
    with open(output_path, 'wb') as f:
        f.write(decrypted)
