import paramiko
import time
import requests

TELEGRAM_TOKEN = '6376514217:AAHxvSy7OB5Da9UVgTK-45y6Az7M1spqMQ4'
TELEGRAM_CHAT_ID = '637620194'
SSH_HOST = '68.50.71.194'
SSH_PORT = 40719
SSH_USER = 'root'
SSH_KEY_PATH = '/Users/st00mp/.ssh/id_rsa'  # Mettez à jour avec le chemin de votre clé privée SSH

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    response = requests.post(url, data=payload)
    return response.json()

def monitor_miner_activity():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, key_filename=SSH_KEY_PATH)

    stdin, stdout, stderr = client.exec_command('htop')
    last_activity = None
    inactivity_threshold = 300  # 5 minutes

    while True:
        output = stdout.readline()
        if 'it/s' in output:
            last_activity = time.time()
        elif last_activity and (time.time() - last_activity) > inactivity_threshold:
            send_telegram_message("Le mineur a cessé de fonctionner (pas d'activité 'it/s').")
            last_activity = None  # Réinitialiser après l'envoi de l'alerte

        time.sleep(60)  # Vérifier toutes les minutes

    client.close()

if __name__ == '__main__':
    monitor_miner_activity()
