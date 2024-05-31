import subprocess
import json
import time
import requests

TELEGRAM_TOKEN = '6376514217:AAHxvSy7OB5Da9UVgTK-45y6Az7M1spqMQ4'
TELEGRAM_CHAT_ID = '637620194'  # Utilisation de l'ID de chat correct
VAST_API_KEY = '8d1cd11f65f38ff2a2cb4fa7098403202d5eca4ad5957be6021a04a1441502c4'

# Fonction pour envoyer des messages Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response.json()

# Configurer la clé API de Vast.ai
def set_vast_api_key(api_key):
    subprocess.run(['vastai', 'set', 'api-key', api_key])

# Clé API de Vast.ai
set_vast_api_key(VAST_API_KEY)

# Fonction pour obtenir les IDs des instances
def get_vast_instance_ids():
    result = subprocess.run(['vastai', 'show', 'instances', '--raw'], capture_output=True, text=True)
    instances = json.loads(result.stdout)
    instance_ids = [instance['id'] for instance in instances]
    print("Instance IDs trouvées:", instance_ids)  # Debug: afficher les IDs des instances
    return instance_ids

# Fonction pour vérifier l'état des instances Vast
def check_vast_instances(instance_ids):
    for instance_id in instance_ids:
        result = subprocess.run(['vastai', 'show', 'instance', str(instance_id), '--raw'], capture_output=True, text=True)
        instance = json.loads(result.stdout)
        print("Détails de l'instance:", instance)  # Debug: afficher les détails de l'instance
        if instance['cur_state'] != 'running':
            message = f"Instance {instance['id']} is {instance['cur_state']}."
            send_telegram_message(message)

# Fonction pour tester l'envoi de notification
def test_telegram_notification():
    message = "Test de notification : le bot Telegram fonctionne correctement."
    response = send_telegram_message(message)
    print("Réponse du test de notification:", response)  # Debug: afficher la réponse de l'API Telegram

# Test de notification
test_telegram_notification()

# Boucle pour vérifier les instances à intervalles réguliers
while True:
    instance_ids = get_vast_instance_ids()
    check_vast_instances(instance_ids)
    time.sleep(300)  # Vérifie toutes les 5 minutes

print("hello")



