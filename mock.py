def mock_vast_instance_data():
    # Mock data simulating low resource utilization
    return {
        'cur_state': 'running',
        'gpu_util': 5,  # Below threshold
        'cpu_util': 0.5,  # Below threshold
        'gpu_temp': 35  # Below threshold
    }


# Function for checking the mocked instance data
def check_mocked_instance():
    instance = mock_vast_instance_data()
    print("Mocked Instance Data:", instance)  # Debug: afficher les détails de l'instance mockée
    if instance['cur_state'] != 'running':
        message = f"Instance {instance['id']} is {instance['cur_state']}."
        send_telegram_message(message)

    # Vérifier les performances du mineur
    gpu_util = instance.get('gpu_util', 0)
    cpu_util = instance.get('cpu_util', 0)
    gpu_temp = instance.get('gpu_temp', 0)

    if gpu_util < 10 or cpu_util < 1 or gpu_temp < 40:
        message = (f"Attention: Le mineur sur l'instance mockée semble être arrêté. "
                   f"Utilisation GPU: {gpu_util}%, Utilisation CPU: {cpu_util}%, Température GPU: {gpu_temp}°C.")
        send_telegram_message(message)


# Call the mock test function instead of the regular check function for testing
check_mocked_instance()
