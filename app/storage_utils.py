import json
import os
import logging
from app.crypto_utils import encrypt_data, decrypt_data

# Set up logging
logger = logging.getLogger(__name__)

# File paths for storing API keys and master wallet addresses
API_KEYS_FILE = "api_keys.json"
MASTER_WALLETS_FILE = "master_wallets.json"

# Save API keys to a JSON file, encrypting each key
def save_api_keys(api_keys):
    """Save the API keys dictionary to a JSON file, encrypting each key."""
    encrypted_api_keys = {k: encrypt_data(v).decode('utf-8') for k, v in api_keys.items()}
    with open(API_KEYS_FILE, "w") as file:
        json.dump(encrypted_api_keys, file)
    masked_api_keys = {k: v[:4] + '...' for k, v in api_keys.items()}
    logger.info(f"Saved API keys: {masked_api_keys}")

# Load and decrypt the API keys from the JSON file
def load_api_keys():
    """Load and decrypt the API keys from the JSON file."""
    if os.path.exists(API_KEYS_FILE):
        try:
            with open(API_KEYS_FILE, "r") as file:
                encrypted_api_keys = json.load(file)
            logger.debug(f"Encrypted API keys loaded: {encrypted_api_keys}")
            api_keys = {k: decrypt_data(v.encode('utf-8')) for k, v in encrypted_api_keys.items()}
            masked_api_keys = {k: v[:4] + '...' for k, v in api_keys.items()}
            logger.info(f"Loaded API keys: {masked_api_keys}")
            return api_keys
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to load API keys: {e}")
            return {}
    logger.info("No API keys file found.")
    return {}

# Save master wallet addresses to a JSON file
def save_master_wallets(master_wallets):
    """Save the master wallets dictionary to a JSON file."""
    encrypted_master_wallets = {k: encrypt_data(v).decode('utf-8') for k, v in master_wallets.items()}
    with open(MASTER_WALLETS_FILE, "w") as file:
        json.dump(encrypted_master_wallets, file)
    masked_master_wallets = {k: v[:4] + '...' for k, v in master_wallets.items()}
    logger.info(f"Saved master wallets: {masked_master_wallets}")

# Load and decrypt the master wallet addresses from the JSON file
def load_master_wallets():
    """Load and decrypt the master wallets from the JSON file."""
    if os.path.exists(MASTER_WALLETS_FILE):
        try:
            with open(MASTER_WALLETS_FILE, "r") as file:
                encrypted_master_wallets = json.load(file)
            logger.debug(f"Encrypted master wallets loaded: {encrypted_master_wallets}")
            master_wallets = {k: decrypt_data(v.encode('utf-8')) for k, v in encrypted_master_wallets.items()}
            masked_master_wallets = {k: v[:4] + '...' for k, v in master_wallets.items()}
            logger.info(f"Loaded master wallets: {masked_master_wallets}")
            return master_wallets
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to load master wallets: {e}")
            return {}
    logger.info("No master wallets file found.")
    return {}
