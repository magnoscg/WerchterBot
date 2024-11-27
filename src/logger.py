import logging
from datetime import datetime, timedelta
from collections import deque
from typing import Dict
from .config import MAX_LOG_BUFFER, MAX_SENT_LOGS_AGE

class TimedLogBuffer:
    """Buffer de logs con limpieza automática"""
    def __init__(self, maxlen: int):
        self.logs = deque(maxlen=maxlen)
        self.sent_logs: Dict[int, datetime] = {}
    
    def append(self, log_entry: dict):
        self.logs.append(log_entry)
    
    def mark_sent(self, log_id: int):
        self.sent_logs[log_id] = datetime.now()
    
    def cleanup_old_logs(self):
        current_time = datetime.now()
        self.sent_logs = {
            log_id: timestamp 
            for log_id, timestamp in self.sent_logs.items()
            if current_time - timestamp < timedelta(seconds=MAX_SENT_LOGS_AGE)
        }

    def get_unsent_logs(self) -> list:
        return [log for log in self.logs if log['id'] not in self.sent_logs]

class MemoryHandler(logging.Handler):
    """Handler personalizado para almacenar logs en memoria"""
    def __init__(self, log_buffer: TimedLogBuffer):
        super().__init__()
        self.log_buffer = log_buffer

    def emit(self, record):
        log_entry = {
            'id': hash(f"{record.created}{record.getMessage()}"),
            'timestamp': datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage()
        }
        self.log_buffer.append(log_entry)

# Inicialización del buffer de logs
log_buffer = TimedLogBuffer(MAX_LOG_BUFFER)

# Configuración del logger
logger = logging.getLogger('WerchterMonitor')
logger.setLevel(logging.INFO)
memory_handler = MemoryHandler(log_buffer)
logger.addHandler(memory_handler)

# Agregar también un handler para la consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(console_handler)