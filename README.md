# Werchter Monitor

Monitor automático para verificar cambios en la página de Rock Werchter.

## Requisitos del Sistema

- Python 3.9 o superior
- systemd (para Linux)
- Acceso a Internet
- Token de bot de Telegram
- ID de chat de Telegram

## Instalación

### 1. Preparación

Clona este repositorio:
```bash
git clone https://your-repo/werchter-monitor.git
cd werchter-monitor
```

### 2. Instalación Automática (Linux)

1. Ejecuta el script de instalación:
```bash
sudo bash scripts/install.sh
```

2. Configura las variables de entorno:
```bash
sudo nano /opt/werchter-monitor/.env
```

3. Inicia el servicio:
```bash
sudo systemctl start werchter-monitor
sudo systemctl enable werchter-monitor
```

### 3. Instalación Manual

1. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Copia y configura el archivo de entorno:
```bash
cp .env.example .env
nano .env  # Edita con tus credenciales
```

4. Ejecuta el monitor:
```bash
python -m werchter_monitor.monitor
```

## Monitoreo y Logs

Los logs se almacenan en:
- Linux (servicio): `/var/log/werchter-monitor/monitor.log`
- Instalación manual: `logs/monitor.log`

Para ver los logs en tiempo real:
```bash
sudo journalctl -u werchter-monitor -f
```

## Mantenimiento

### Actualización

1. Detén el servicio:
```bash
sudo systemctl stop werchter-monitor
```

2. Actualiza el código:
```bash
cd /opt/werchter-monitor
git pull
```

3. Actualiza dependencias:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. Reinicia el servicio:
```bash
sudo systemctl restart werchter-monitor
```

### Backup

Los archivos importantes a respaldar son:
- Archivo de configuración: `.env`
- Logs: `/var/log/werchter-monitor/`

## Solución de Problemas

1. Verificar estado del servicio:
```bash
sudo systemctl status werchter-monitor
```

2. Verificar logs:
```bash
sudo journalctl -u werchter-monitor -n 100
```

3. Problemas comunes:
- Error de permisos: Verificar propietario de archivos
- Error de conexión: Verificar conectividad a Internet
- Error de Telegram: Verificar token y chat ID

## Seguridad

- Las credenciales se almacenan en `.env`
- Los logs rotan automáticamente
- El servicio se ejecuta con un usuario dedicado
- Permisos restrictivos en archivos de configuración

## Soporte

Para reportar problemas o sugerencias:
1. Abre un issue en el repositorio
2. Incluye logs relevantes
3. Describe el problema en detalle