import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

from src.logger import logger, log_buffer
from src.monitor import start_monitor
from src.config import LOG_CLEANUP_INTERVAL
from src.web.websocket import ws_manager
from src.web.templates import HTML_TEMPLATE

app = FastAPI()

async def cleanup_logs():
    while True:
        await asyncio.sleep(LOG_CLEANUP_INTERVAL)
        log_buffer.cleanup_old_logs()

@app.on_event("startup")
async def startup_event():
    app.state.monitor_task = asyncio.create_task(start_monitor())
    app.state.cleanup_task = asyncio.create_task(cleanup_logs())

@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, 'monitor_task'):
        app.state.monitor_task.cancel()
        try:
            await app.state.monitor_task
        except asyncio.CancelledError:
            pass
    
    if hasattr(app.state, 'cleanup_task'):
        app.state.cleanup_task.cancel()
        try:
            await app.state.cleanup_task
        except asyncio.CancelledError:
            pass

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_TEMPLATE

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        if not await ws_manager.connect(websocket):
            return
        
        # Enviar logs existentes
        for log in list(log_buffer.logs):
            await websocket.send_text(json.dumps(log))
            log_buffer.mark_sent(log['id'])
        
        try:
            while True:
                # Esperar más tiempo entre actualizaciones
                await asyncio.sleep(5)
                # Solo enviar nuevos logs
                new_logs = log_buffer.get_unsent_logs()
                for log in new_logs:
                    await websocket.send_text(json.dumps(log))
                    log_buffer.mark_sent(log['id'])
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")
        finally:
            ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error en websocket: {str(e)}")
        ws_manager.disconnect(websocket)