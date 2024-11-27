# Werchter Monitor

Monitor automático para verificar cambios en la página de Rock Werchter.

## Configuración de Variables de Entorno

El proyecto requiere dos variables de entorno:

- `TELEGRAM_BOT_TOKEN`: El token de tu bot de Telegram
- `TELEGRAM_CHAT_ID`: El ID del chat donde se enviarán los mensajes

### Obtener las Credenciales

1. **Para obtener el BOT_TOKEN:**
   - Habla con [@BotFather](https://t.me/botfather) en Telegram
   - Usa el comando `/newbot`
   - Sigue las instrucciones para crear un nuevo bot
   - BotFather te dará un token que se ve así: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

2. **Para obtener el CHAT_ID:**
   - Añade tu bot al grupo donde quieres recibir las notificaciones
   - Envía cualquier mensaje al grupo
   - Visita: `https://api.telegram.org/bot<YourBOTToken>/getUpdates`
   - Busca el "chat":{"id": -XXXXXXXXX} en la respuesta
   - El número (incluyendo el signo negativo si está presente) es tu CHAT_ID

## Despliegue en Render

1. **Preparación:**
   - Haz fork de este repositorio en GitHub
   - Crea una cuenta en [Render](https://render.com)

2. **Crear Nuevo Servicio:**
   - Ve al Dashboard de Render
   - Click en "New +"
   - Selecciona "Background Worker"
   - Conecta tu repositorio de GitHub

3. **Configuración del Servicio:**
   - Nombre: `werchter-monitor` (o el que prefieras)
   - Environment: `Python`
   - Region: Selecciona la más cercana a ti
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python werchter.py`

4. **Configurar Variables de Entorno:**
   - En la sección "Environment Variables"
   - Añade `TELEGRAM_BOT_TOKEN` con tu token de bot
   - Añade `TELEGRAM_CHAT_ID` con tu ID de chat
   - Marca ambas variables como "Secret"

5. **Desplegar:**
   - Click en "Create Background Worker"
   - Render desplegará automáticamente tu servicio

### Verificar el Despliegue

1. Ve a la pestaña "Logs" en Render
2. Deberías ver mensajes de inicio del bot
3. Verifica en tu grupo de Telegram que recibes el mensaje de inicio

### Solución de Problemas

Si no recibes mensajes, verifica:

1. **Variables de Entorno:**
   ```bash
   # En los logs de Render, deberías ver algo como:
   Bot validado: @tu_bot_name
   ```

2. **Permisos del Bot:**
   - El bot debe ser administrador del grupo
   - Debe tener permisos para enviar mensajes

3. **Formato del CHAT_ID:**
   - Para grupos, debe incluir el signo negativo
   - Ejemplo: `-1234567890`

## Desarrollo Local

Para probar localmente antes de desplegar:

1. Crea un archivo `.env`:
   ```bash
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta:
   ```bash
   python werchter.py
   ```

## Mantenimiento

- Los logs están disponibles en el dashboard de Render
- Render redesplegará automáticamente cuando haya cambios en la rama main
- Puedes configurar alertas en Render para problemas de despliegue