import asyncio
import aiohttp
from bs4 import BeautifulSoup
import backoff
from typing import Optional, Tuple
from datetime import datetime

from src.config import TelegramConfig, WERCHTER_URL, TARGET_PHRASE, CHECK_INTERVAL
from src.logger import logger

class TelegramMonitor:
    """Clase principal para monitorear cambios y enviar notificaciones"""
    def __init__(self):
        self.config = TelegramConfig.from_env()
        self.session: Optional[aiohttp.ClientSession] = None
        self.check_interval = CHECK_INTERVAL
        self._stop_event = asyncio.Event()
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def stop(self):
        """Detener el monitor de forma segura"""
        self._stop_event.set()

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=5
    )
    async def send_message(self, message: str) -> bool:
        """Enviar mensaje a Telegram con reintentos exponenciales"""
        if not self.session:
            raise RuntimeError("La sesión HTTP no está inicializada")
            
        try:
            url = f"{self.config.base_url}/sendMessage"
            payload = {
                "chat_id": self.config.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            async with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                logger.info("Mensaje enviado correctamente a Telegram")
                return True
                
        except Exception as e:
            logger.error(f"Error enviando mensaje a Telegram: {str(e)}")
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
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(WERCHTER_URL, headers=headers) as response:
                response.raise_for_status()
                page_content = await response.text()
                
            soup = BeautifulSoup(page_content, 'html.parser')
            page_text = soup.get_text()
            phrase_present = TARGET_PHRASE in page_text
            
            status_message = "No hay cambios nuevos" if phrase_present else "¡Hay cambios nuevos!"
            logger.info(f"Verificación completada. {status_message}")
            return phrase_present, page_text
            
        except Exception as e:
            logger.error(f"Error verificando la página: {str(e)}")
            raise

    async def run(self):
        """Ejecutar el monitor de forma asíncrona"""
        logger.info("Iniciando monitoreo...")
        await self.send_message("🚀 Monitor iniciado!\nVerificando cambios en Rock Werchter...")
        
        last_state = None
        check_count = 0
        
        while not self._stop_event.is_set():
            try:
                current_state, page_text = await self.check_website()
                check_count += 1
                
                if current_state is not None:
                    if last_state is not None and current_state != last_state:
                        message = (
                            "🔔 <b>¡Cambio detectado en Rock Werchter!</b>\n\n"
                            "La página ha sido actualizada.\n"
                            f"Verifica los cambios en:\n{WERCHTER_URL}"
                        )
                        await self.send_message(message)
                    
                    last_state = current_state
                
                if check_count % 12 == 0:
                    cambios = "SÍ ha habido cambios" if last_state != current_state else "NO ha habido cambios"
                    estado_actual = "La caseta de perro esta lista" if not current_state else "Hay que ir pensando en sacos de dormir."
                    
                    await self.send_message(
                        f"🔄 Reporte de Estado:\n\n"
                        f"📊 Verificaciones realizadas: {check_count}\n"
                        f"🔍 Cambios detectados: {cambios}\n"
                        f"📌 Estado actual: {estado_actual}\n"
                        f"⏰ Última verificación: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n\n"
                        f"🌐 Monitor funcionando correctamente..."
                    )
                
                # Esperar con timeout para poder interrumpir
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self.check_interval
                    )
                except asyncio.TimeoutError:
                    continue
                
            except Exception as e:
                logger.error(f"Error en el ciclo principal: {str(e)}")
                await self.send_message(f"⚠️ <b>Error en el monitor</b>\n{str(e)}\nReintentando en 1 minuto...")
                await asyncio.sleep(60)