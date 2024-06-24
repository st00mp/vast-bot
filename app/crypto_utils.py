from cryptography.fernet import Fernet
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Generate a new encryption key and save it to a file (do this once)
def generate_key():
    """Generate a new encryption key and save it to a file."""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    logger.info("Generated new encryption key.")

# Load the encryption key from a file
def load_key():
    """Load the previously generated encryption key from a file."""
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'secret.key')
    key = open(key_path, "rb").read()
    logger.info("Loaded encryption key.")
    return key

# Encrypt data using the loaded encryption key
def encrypt_data(data):
    """Encrypt a message using the loaded encryption key."""
    key = load_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    logger.info(f"Encrypted data: {data[:4]}... -> {encrypted_data[:10]}...")
    return encrypted_data

# Decrypt data using the loaded encryption key
def decrypt_data(encrypted_data):
    """Decrypt an encrypted message using the loaded encryption key."""
    key = load_key()
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    logger.info(f"Decrypted data: {encrypted_data[:10]}... -> {decrypted_data[:4]}...")
    return decrypted_data