import os

import requests
from dotenv import load_dotenv

from src.utils.logger import setup_logger

logger = setup_logger(__name__)
load_dotenv()


class TelegramSender:
    """Handles sending notifications via Telegram."""

    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    def send_message(self, message: str) -> bool:
        """Sends a message to the configured Telegram chat."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials missing. Skipping notification.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {"chat_id": self.chat_id, "text": message}

        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logger.info("Message sent to Telegram!")
                return True
            else:
                logger.error(f"Telegram failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
