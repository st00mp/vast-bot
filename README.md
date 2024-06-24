# Vast.ai Notification Bot

## Description
This project is a Telegram bot that monitors and notifies the user about the status of Vast.ai instances. It offers functionalities such as checking the credit balance, retrieving detailed information about instances, and monitoring GPU and CPU utilization. The bot can also check the balance of a Nimble wallet. User API keys for Vast.ai are encrypted and securely stored on the server.

## Features
- **API Key Management**: Add or remove your Vast.ai API key.
- **Instance Monitoring**: Get detailed information about your Vast.ai instances.
- **Credit Balance Check**: Check your Vast.ai account credit balance.
- **Nimble Wallet Management**: Add, remove, and check the balance of your Nimble wallet.
- **Automatic Notifications**: Receive notifications when your instances have unusually low GPU or CPU usage.
- **Secure Storage**: User API keys are encrypted and securely stored on the server.

## Technologies
- Python
- Telegram Bot API
- Vast.ai API
- Nimble API
- dotenv
- requests
- subprocess
- logging
- threading

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/vastai-notification-bot.git
    ```
2. Navigate to the project directory:
    ```sh
    cd vastai-notification-bot
    ```
3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Configure the environment variables:
    - Create a `.env` file in the project's root directory.
    - Add your Telegram token:
        ```
        TELEGRAM_TOKEN=your_telegram_token
        ```

## Usage
1. Start the bot:
    ```sh
    python main.py
    ```
2. Use the following commands in your Telegram chat with the bot:
    - `/setapikey`: Set your Vast.ai API key.
    - `/removeapikey`: Remove your Vast.ai API key.
    - `/infos`: Get information about your Vast.ai instances.
    - `/credit`: Check your Vast.ai account credit balance.
    - `/setmasterwallet`: Set your Nimble master wallet address.
    - `/removemasterwallet`: Remove your Nimble master wallet address.
    - `/checknimbalance`: Check your Nimble wallet balance.
    - `/start`: Display the help message.

## Example Commands
- **Set API Key**:
    ```
    /setapikey
    ```
    Then, send your API key in the chat.

- **Get Instance Information**:
    ```
    /infos
    ```

- **Check Credit Balance**:
    ```
    /credit
    ```

- **Set Nimble Wallet Address**:
    ```
    /setmasterwallet
    ```
    Then, send your Nimble wallet address in the chat.

## Contributions
Contributions are welcome! Please submit a pull request or open an issue to discuss the changes you want to make.

## Authors
- st00mp (https://github.com/st00mp)
