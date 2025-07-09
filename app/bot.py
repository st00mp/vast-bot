from dotenv import load_dotenv
import os
import subprocess
import json
import time
import requests
import re
import logging
from threading import Thread
from app.storage_utils import save_api_keys, load_api_keys, save_master_wallets, load_master_wallets

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Retrieve Telegram token from environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables")

# Load API keys and master wallet addresses at startup
VAST_API_KEYS = load_api_keys()
MASTER_WALLETS = load_master_wallets()
REGISTERED_CHAT_IDS = set()
IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'vast-notification-bot-help-api.png')
AWAITING_API_KEY = set()
AWAITING_MASTER_WALLET = set()

def send_telegram_message(message, chat_id):
    """Send a message to a Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    response = requests.post(url, data=payload)
    return response.json()

def send_telegram_image(image_path, caption, chat_id):
    """Send an image with a caption to a Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(image_path, 'rb') as image_file:
        payload = {'chat_id': chat_id, 'caption': caption}
        files = {'photo': image_file}
        response = requests.post(url, data=payload, files=files)
    return response.json()

def is_valid_api_key(api_key):
    """Check if the provided API key is valid."""
    return bool(re.match(r'^[a-f0-9]{64}$', api_key))

def set_vast_api_key(chat_id, api_key):
    """Set the Vast.ai API key for a specific chat ID."""
    if is_valid_api_key(api_key):
        VAST_API_KEYS[chat_id] = api_key
        save_api_keys(VAST_API_KEYS)
        return True
    return False

def remove_vast_api_key(chat_id):
    """Remove the Vast.ai API key for a specific chat ID."""
    if chat_id in VAST_API_KEYS:
        del VAST_API_KEYS[chat_id]
        save_api_keys(VAST_API_KEYS)
        return True
    return False

def get_vast_instance_ids(api_key):
    """Retrieve instance IDs from Vast.ai using the provided API key."""
    result = subprocess.run(['vastai', 'set', 'api-key', api_key], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Error setting API key: {result.stderr}")
        return []

    result = subprocess.run(['vastai', 'show', 'instances', '--raw'], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Error showing instances: {result.stderr}")
        return []

    instances = json.loads(result.stdout)
    instance_ids = [instance['id'] for instance in instances]
    logger.info("Instance IDs found: %s", instance_ids)
    return instance_ids

def check_credit_balance(api_key):
    """Check the credit balance for a given Vast.ai API key."""
    result = subprocess.run(['vastai', 'set', 'api-key', api_key], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Error setting API key: {result.stderr}")
        return 0

    result = subprocess.run(['vastai', 'show', 'user', '--raw'], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Error showing user info: {result.stderr}")
        return 0

    user_info = json.loads(result.stdout)
    credit_balance = round(user_info.get('credit', 0), 2)
    logger.info("Credit balance: %s", credit_balance)
    return credit_balance

def check_vast_instances(api_key):
    """Check the status of Vast.ai instances and identify problematic ones."""
    problematic_instances = []
    instance_ids = get_vast_instance_ids(api_key)

    for instance_id in instance_ids:
        result = subprocess.run(['vastai', 'show', 'instance', str(instance_id), '--raw'], capture_output=True,
                                text=True)
        if result.returncode != 0:
            logger.error(f"Error showing instance {instance_id}: {result.stderr}")
            continue

        instance = json.loads(result.stdout)
        logger.info("Instance details: %s", instance)

        if instance['cur_state'] != 'running':
            problematic_instances.append(instance_id)

        gpu_util = instance.get('gpu_util', 0)
        cpu_util = instance.get('cpu_util', 0)
        gpu_temp = instance.get('gpu_temp', 0)

        if gpu_util < 10 or cpu_util < 1 or gpu_temp < 40:
            problematic_instances.append(instance_id)

    return problematic_instances

def get_instance_info(api_key):
    """Get detailed information about Vast.ai instances for a given API key."""
    instance_ids = get_vast_instance_ids(api_key)
    info_messages = []
    for instance_id in instance_ids:
        result = subprocess.run(['vastai', 'show', 'instance', str(instance_id), '--raw'], capture_output=True,
                                text=True)
        if result.returncode != 0:
            logger.error(f"Error showing instance {instance_id}: {result.stderr}")
            continue

        instance = json.loads(result.stdout)
        info_message = (f"🆔 Instance ID: {instance_id}\n"
                        f"🏷 Label: {instance.get('label', 'No label')}\n"
                        f"📈 State: {instance.get('cur_state', 'Unknown')}\n"
                        f"🖥 GPU Utilization: {instance.get('gpu_util', 'N/A')}%\n"
                        f"💻 CPU Utilization: {instance.get('cpu_util', 'N/A')}%\n"
                        f"🌡 GPU Temperature: {instance.get('gpu_temp', 'N/A')}°C")
        info_messages.append(info_message)
    return "\n\n".join(info_messages)

def check_nim_balance(wallet_address):
    """Check the balance of a Nimble wallet."""
    url = 'https://mainnet.nimble.technology/check_balance'
    headers = {'Content-Type': 'application/json'}
    data = {'address': wallet_address}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        balance_data = response.json()
        return balance_data.get('msg', 'No balance information available.')
    else:
        return 'Failed to retrieve balance information.'

def handle_telegram_updates():
    """Handle updates from Telegram."""
    last_update_id = None
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {'timeout': 100, 'offset': last_update_id}

    while True:
        try:
            response = requests.get(url, params=params)
            updates = response.json().get('result', [])

            for update in updates:
                last_update_id = update['update_id'] + 1
                message = update.get('message', {})
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')

                if text == '/setapikey':
                    AWAITING_API_KEY.add(chat_id)
                    caption = ("Please send your API key in the next message.\n"
                               "You will find your API key on https://cloud.vast.ai/account/ under 'API Keys'.")
                    send_telegram_image(IMAGE_PATH, caption, chat_id)
                elif chat_id in AWAITING_API_KEY and not text.startswith('/'):
                    if set_vast_api_key(chat_id, text.strip()):
                        AWAITING_API_KEY.remove(chat_id)
                        send_telegram_message("Your API key has been set successfully.", chat_id)
                    else:
                        send_telegram_message("Invalid API key format. Please try again.", chat_id)
                elif text == '/removeapikey':
                    if remove_vast_api_key(chat_id):
                        send_telegram_message("Your API key has been removed successfully.", chat_id)
                    else:
                        send_telegram_message("No API key found to remove.", chat_id)
                elif text == '/setmasterwallet':
                    AWAITING_MASTER_WALLET.add(chat_id)
                    send_telegram_message("Please send your master wallet address in the next message.", chat_id)
                elif chat_id in AWAITING_MASTER_WALLET and not text.startswith('/'):
                    MASTER_WALLETS[chat_id] = text.strip()
                    save_master_wallets(MASTER_WALLETS)
                    AWAITING_MASTER_WALLET.remove(chat_id)
                    send_telegram_message("Your master wallet address has been set successfully.", chat_id)
                elif text == '/checknimbalance':
                    if chat_id in MASTER_WALLETS:
                        balance_message = check_nim_balance(MASTER_WALLETS[chat_id])
                        send_telegram_message(balance_message, chat_id)
                    else:
                        send_telegram_message("Please set your master wallet address using /setmasterwallet.", chat_id)
                elif text == '/removemasterwallet':
                    if chat_id in MASTER_WALLETS:
                        del MASTER_WALLETS[chat_id]
                        save_master_wallets(MASTER_WALLETS)
                        send_telegram_message("Your master wallet address has been removed successfully.", chat_id)
                    else:
                        send_telegram_message("No master wallet address found to remove.", chat_id)
                elif text == '/credit':
                    if chat_id in VAST_API_KEYS:
                        credit_balance = check_credit_balance(VAST_API_KEYS[chat_id])
                        send_telegram_message(f"Your credit balance is {credit_balance} euros.", chat_id)
                    else:
                        send_telegram_message("Please set your API key using /setapikey.", chat_id)
                elif text == '/infos':
                    if chat_id in VAST_API_KEYS:
                        info_message = get_instance_info(VAST_API_KEYS[chat_id])
                        send_telegram_message(info_message, chat_id)
                    else:
                        send_telegram_message("Please set your API key using /setapikey.", chat_id)
                elif text == '/start':
                    REGISTERED_CHAT_IDS.add(chat_id)
                    start_message = (
                        "🤖 *Welcome to the Vast.ai Notification Bot!*\n\n"
                        "This bot will automatically notify you when your instance seems to have stopped.\n\n"
                        "You can also check various information using different commands:\n\n"
                        "🔹 /setapikey - Set your Vast.ai API key\n"
                        "🔹 /removeapikey - Remove your current API key\n"
                        "📊 /infos - Get detailed information about your instances\n"
                        "💰 /credit - Check your current credit balance\n"
                        "🔹 /setmasterwallet - Set your Nimble master wallet address\n"
                        "🔹 /removemasterwallet - Remove your Nimble master wallet address\n"
                        "🔹 /checknimbalance - Check your Nimble wallet balance\n"
                        "🚀 /start - Display this help message"
                    )
                    send_telegram_message(start_message, chat_id)

            params['offset'] = last_update_id
        except Exception as e:
            logger.error(f"Error in handle_telegram_updates: {e}")
            time.sleep(5)

def monitor_instances():
    """Monitor Vast.ai instances and send alerts if any issues are detected."""
    idle_check_counter = {}

    while True:
        try:
            for chat_id, api_key in VAST_API_KEYS.items():
                logger.debug(f"Checking instances for chat_id: {chat_id}, api_key: {api_key[:4]}...")
                problematic_instances = check_vast_instances(api_key)

                for instance_id in problematic_instances:
                    if instance_id in idle_check_counter:
                        idle_check_counter[instance_id] += 1
                    else:
                        idle_check_counter[instance_id] = 1

                    if idle_check_counter[instance_id] >= 2:
                        message = f"Attention: The miner on instance {instance_id} seems to be stopped."
                        send_telegram_message(message, chat_id)
                    if idle_check_counter[instance_id] >= 6:  # Alert if GPU usage is <= 60% for 1 hour
                        message = f"Recommendation: Consider restarting instance {instance_id} due to low GPU usage."
                        send_telegram_message(message, chat_id)
                for instance_id in list(idle_check_counter):
                    if instance_id not in problematic_instances:
                        del idle_check_counter[instance_id]

            time.sleep(600)
        except Exception as e:
            logger.error(f"Error in monitor_instances: {e}")
            time.sleep(10)

def start_bot():
    """Start the Telegram bot and instance monitoring."""
    Thread(target=handle_telegram_updates).start()
    Thread(target=monitor_instances).start()

if __name__ == '__main__':
    start_bot()
