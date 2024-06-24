import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    """Configuration class to hold application settings."""
    # Retrieve the Telegram token from environment variables
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

    # Ensure TELEGRAM_TOKEN is set
    if TELEGRAM_TOKEN is None:
        raise ValueError("No TELEGRAM_TOKEN set for Flask application. Did you follow the setup instructions?")
