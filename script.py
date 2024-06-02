import subprocess
import json
import time
import requests
import os

TELEGRAM_TOKEN = '6376514217:AAHxvSy7OB5Da9UVgTK-45y6Az7M1spqMQ4'
VAST_API_KEYS = {}  # Dictionary to store API keys for each user
REGISTERED_CHAT_IDS = set()  # Set to store registered chat IDs
IMAGE_PATH = '/home/ec2-user/vast-notification-bot-help-api.png'
AWAITING_API_KEY = set()  # Set to track users who need to send their API key

# Function to send Telegram messages
def send_telegram_message(message, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    response = requests.post(url, data=payload)
    return response.json()

# Function to send images to Telegram
def send_telegram_image(image_path, caption, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(image_path, 'rb') as image_file:
        payload = {'chat_id': chat_id, 'caption': caption}
        files = {'photo': image_file}
        response = requests.post(url, data=payload, files=files)
    return response.json()

# Function to set the Vast.ai API key for a user
def set_vast_api_key(chat_id, api_key):
    VAST_API_KEYS[chat_id] = api_key

# Function to get instance IDs for a user
def get_vast_instance_ids(api_key):
    result = subprocess.run(['vastai', 'set', 'api-key', api_key], capture_output=True, text=True)
    result = subprocess.run(['vastai', 'show', 'instances', '--raw'], capture_output=True, text=True)
    instances = json.loads(result.stdout)
    instance_ids = [instance['id'] for instance in instances]
    print("Instance IDs found:", instance_ids)  # Debug: display instance IDs
    return instance_ids

# Function to check credit balance for a user
def check_credit_balance(api_key):
    result = subprocess.run(['vastai', 'set', 'api-key', api_key], capture_output=True, text=True)
    result = subprocess.run(['vastai', 'show', 'user', '--raw'], capture_output=True, text=True)
    user_info = json.loads(result.stdout)
    credit_balance = round(user_info.get('credit', 0), 2)
    print("Credit balance:", credit_balance)  # Debug: display credit balance
    return credit_balance

# Function to check instance status and performance for a user
def check_vast_instances(api_key):
    problematic_instances = []
    instance_ids = get_vast_instance_ids(api_key)

    for instance_id in instance_ids:
        result = subprocess.run(['vastai', 'show', 'instance', str(instance_id), '--raw'], capture_output=True,
                                text=True)
        instance = json.loads(result.stdout)
        print("Instance details:", instance)  # Debug: display instance details

        if instance['cur_state'] != 'running':
            problematic_instances.append(instance_id)

        # Check miner performance
        gpu_util = instance.get('gpu_util', 0)
        cpu_util = instance.get('cpu_util', 0)
        gpu_temp = instance.get('gpu_temp', 0)

        if gpu_util < 10 or cpu_util < 1 or gpu_temp < 40:
            problematic_instances.append(instance_id)

    return problematic_instances

# Function to get and format instance information for a user
def get_instance_info(api_key):
    instance_ids = get_vast_instance_ids(api_key)
    info_messages = []
    for instance_id in instance_ids:
        result = subprocess.run(['vastai', 'show', 'instance', str(instance_id), '--raw'], capture_output=True,
                                text=True)
        instance = json.loads(result.stdout)
        info_message = (f"🆔 Instance ID: {instance_id}\n"
                        f"🏷 Label: {instance.get('label', 'No label')}\n"
                        f"📈 State: {instance.get('cur_state', 'Unknown')}\n"
                        f"🖥 GPU Utilization: {instance.get('gpu_util', 'N/A')}%\n"
                        f"💻 CPU Utilization: {instance.get('cpu_util', 'N/A')}%\n"
                        f"🌡 GPU Temperature: {instance.get('gpu_temp', 'N/A')}°C")
        info_messages.append(info_message)
    return "\n\n".join(info_messages)

# Function to handle Telegram updates
def handle_telegram_updates():
    last_update_id = None
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {'timeout': 100, 'offset': last_update_id}

    while True:
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
                set_vast_api_key(chat_id, text)
                AWAITING_API_KEY.remove(chat_id)
                send_telegram_message("Your API key has been set successfully.", chat_id)
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
                start_message = ("🤖 *Welcome to the Vast.ai Notification Bot!*\n\n"
                                 "This bot will automatically notify you when your instance seems to have stopped. "
                                 "You can also check various information using different commands:\n"
                                 "🔹 /setapikey - Set your Vast.ai API key\n"
                                 "📊 /infos - Get detailed information about your instances\n"
                                 "💰 /credit - Check your current credit balance\n"
                                 "🚀 /start - Display this help message")
                send_telegram_message(start_message, chat_id)

        params['offset'] = last_update_id

# Function to test notification sending
def test_telegram_notification():
    for chat_id in REGISTERED_CHAT_IDS:
        message = "Notification test: the Telegram bot is working correctly."
        response = send_telegram_message(message, chat_id)
        print("Notification test response:", response)  # Debug: display API response

# Notification test
test_telegram_notification()

# Loop to check instances and handle commands at regular intervals
idle_check_counter = {}

while True:
    for chat_id, api_key in VAST_API_KEYS.items():
        problematic_instances = check_vast_instances(api_key)

        for instance_id in problematic_instances:
            if instance_id in idle_check_counter:
                idle_check_counter[instance_id] += 1
            else:
                idle_check_counter[instance_id] = 1

            if idle_check_counter[instance_id] >= 2:  # Trigger alert if issue persists for 2 consecutive checks (20 minutes)
                message = f"Attention: The miner on instance {instance_id} seems to be stopped."
                send_telegram_message(message, chat_id)
        for instance_id in list(idle_check_counter):
            if instance_id not in problematic_instances:
                del idle_check_counter[instance_id]  # Reset counter if instance is back to normal

    handle_telegram_updates()  # Handle Telegram commands
    time.sleep(600)  # Check every 10 minutes
