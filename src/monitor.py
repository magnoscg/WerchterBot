import asyncio
import signal
import sys
from src.telegram_bot import TelegramMonitor
from src.logger import logger

async def start_monitor():
    """Iniciar el monitor como una tarea asíncrona"""
    async with TelegramMonitor() as monitor:
        await monitor.run()

def signal_handler(sig, frame):
    """Manejador de señales para terminar limpiamente"""
    logger.info("Recibida señal de terminación. Cerrando aplicación...")
    sys.exit(0)

def setup_signal_handlers():
    """Configurar manejadores de señales"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    setup_signal_handlers()
    asyncio.run(start_monitor())