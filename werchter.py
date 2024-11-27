import asyncio
import os
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional, Tuple
import backoff

# Cargar variables de entorno
load_dotenv()

@dataclass
class TelegramConfig:
    """Configuración para el bot de Telegram"""
    bot_token: str
    chat_id: str
    base_url: str

    @classmethod
    def from_env(cls) -> 'TelegramConfig':
        """Crear configuración desde variables de entorno"""
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            raise ValueError("Las variables de entorno TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID son requeridas")
        
        return cls(
            bot_token=bot_token,
            chat_id=chat_id,
            base_url=f"https://api.telegram.org/bot{bot_token}"
        )

class LoggerSetup:
    """Configuración del sistema de logging"""
    @staticmethod
    def setup() -> logging.Logger:
        logger = logging.getLogger('WerchterMonitor')
        logger.setLevel(logging.INFO)
        
        # Formato del log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para archivo con rotación
        file_handler = RotatingFileHandler(
            'monitor.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

class TelegramMonitor:
    def __init__(self):
        self.config = TelegramConfig.from_env()
        self.logger = LoggerSetup.setup()
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Crear sesión HTTP al entrar en el contexto"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cerrar sesión HTTP al salir del contexto"""
        if self.session:
            await self.session.close()
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=5
    )
    async def send_message(self, message: str) -> bool:
        """
        Enviar mensaje a Telegram con reintentos exponenciales
        """
        if not self.session:
            raise RuntimeError("La sesión HTTP no está inicializada")
            
        try:
            url = f"{self.config.base_url}/sendMessage"
            payload = {
                "chat_id": self.config.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            async with self.session.post(url, json=payload, timeout=30) as response:
                response.raise_for_status()
                self.logger.info("Mensaje enviado correctamente a Telegram")
                return True
                
        except aiohttp.ClientResponseError as e:
            self.logger.error(f"Error de respuesta de Telegram: {e.status} - {e.message}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado enviando mensaje: {e}")
            raise

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3
    )
    async def check_website(self) -> Tuple[Optional[bool], Optional[str]]:
        """Verificar cambios en la página web con reintentos"""
        if not self.session:
            raise RuntimeError("La sesión HTTP no está inicializada")
            
        url = "https://www.rockwerchter.be/en/info/camping/the-hive-resort"
        target_phrase = "Packages for The Hive Resort will be available soon"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers, timeout=30) as response:
                response.raise_for_status()
                page_content = await response.text()
                
            soup = BeautifulSoup(page_content, 'html.parser')
            page_text = soup.get_text()
            phrase_present = target_phrase in page_text
            
            self.logger.info(f"Verificación completada. Frase encontrada: {phrase_present}")
            return phrase_present, page_text
            
        except aiohttp.ClientResponseError as e:
            self.logger.error(f"Error de respuesta del sitio web: {e.status} - {e.message}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado verificando la página: {e}")
            raise

    async def run(self):
        """Ejecutar el monitor de forma asíncrona"""
        self.logger.info("Iniciando monitoreo...")
        await self.send_message("🚀 Monitor iniciado!\nVerificando cambios en Rock Werchter...")
        
        last_state = None
        check_count = 0
        
        while True:
            try:
                current_state, page_text = await self.check_website()
                check_count += 1
                
                if current_state is not None:
                    if last_state is not None and current_state != last_state:
                        message = (
                            "🔔 <b>¡Cambio detectado en Rock Werchter!</b>\n\n"
                            "La página ha sido actualizada.\n"
                            "Verifica los cambios en:\n"
                            "https://www.rockwerchter.be/en/info/camping/the-hive-resort"
                        )
                        await self.send_message(message)
                    
                    last_state = current_state
                
                # Enviar reporte cada 12 verificaciones
                if check_count % 12 == 0:
                    cambios = "Ha habido cambios" if last_state != current_state else "NO ha habido cambios"
                    estado_actual = "La caseta de perro esta lista" if not current_state else "Hay que ir pensando en sacos de dormir."
                    
                    await self.send_message(
                        f"🔄 Reporte de Estado:\n\n"
                        f"📊 Verificaciones realizadas: {check_count}\n"
                        f"🔍 Cambios detectados: {cambios}\n"
                        f"📌 Estado actual: {estado_actual}\n"
                        f"⏰ Última verificación: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n\n"
                        f"🌐 Monitor funcionando correctamente..."
                    )
                
                # Esperar de forma asíncrona
                await asyncio.sleep(600)  # 10 minutos
                
            except Exception as e:
                self.logger.error(f"Error en el ciclo principal: {e}")
                await self.send_message(f"⚠️ <b>Error en el monitor</b>\n{str(e)}\nReintentando en 1 minuto...")
                await asyncio.sleep(60)

async def main():
    """Función principal asíncrona"""
    async with TelegramMonitor() as monitor:
        await monitor.run()

if __name__ == "__main__":
    # Ejecutar el loop de eventos
    asyncio.run(main())