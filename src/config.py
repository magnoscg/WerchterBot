import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de constantes
MAX_LOG_BUFFER = 1000
MAX_WEBSOCKET_CLIENTS = 100
WEBSOCKET_TIMEOUT = 60  # segundos
LOG_CLEANUP_INTERVAL = 3600  # 1 hora
MAX_SENT_LOGS_AGE = 3600  # 1 hora
CHECK_INTERVAL = 600  # 10 minutos entre verificaciones
DEFAULT_PORT = 8000

@dataclass
class TelegramConfig:
    """Configuración para el bot de Telegram"""
    bot_token: str
    chat_id: str
    base_url: str

    @classmethod
    def from_env(cls) -> 'TelegramConfig':
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            raise ValueError("Variables de entorno TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID requeridas")
        
        return cls(
            bot_token=bot_token,
            chat_id=chat_id,
            base_url=f"https://api.telegram.org/bot{bot_token}"
        )

# URLs y textos constantes
WERCHTER_URL = "https://www.rockwerchter.be/en/info/camping/the-hive-resort"
TARGET_PHRASE = "Packages for The Hive Resort will be available soon"