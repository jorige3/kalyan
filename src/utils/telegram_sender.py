import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_message(message: str):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("❌ Telegram credentials missing! Ensure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set in .env")
        return False

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
    response = requests.post(url, data=data)

    if response.status_code == 200:
        print("✅ Message sent to Telegram!")
        return True
    else:
        print(f"❌ Telegram failed: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    # Example usage for testing
    test_message = "Hello from telegram_sender.py! This is a test message."
    send_telegram_message(test_message)
