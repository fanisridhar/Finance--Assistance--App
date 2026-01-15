from cryptography.fernet import Fernet
import os
import base64
from dotenv import load_dotenv

load_dotenv()

# Generate or use existing encryption key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a new key if not set (for development only)
    key = Fernet.generate_key()
    ENCRYPTION_KEY = key.decode()
    print(f"WARNING: Generated new encryption key. Set ENCRYPTION_KEY={ENCRYPTION_KEY} in .env")

if ENCRYPTION_KEY:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode())
else:
    cipher_suite = None

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data like Plaid access tokens"""
    if not data or not cipher_suite:
        return data
    encrypted_data = cipher_suite.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data or not cipher_suite:
        return encrypted_data
    try:
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = cipher_suite.decrypt(decoded_data)
        return decrypted_data.decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")

