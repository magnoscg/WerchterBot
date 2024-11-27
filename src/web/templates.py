HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Werchter Monitor</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px;
            background-color: #f5f5f5;
        }
        #log { 
            height: 500px; 
            overflow-y: auto; 
            border: 1px solid #ddd; 
            padding: 10px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .log-entry {
            margin: 5px 0;
            padding: 5px;
            border-bottom: 1px solid #eee;
            font-family: monospace;
        }
        .INFO { color: #2196F3; }
        .ERROR { color: #f44336; }
        .WARNING { color: #ff9800; }
        h1 {
            color: #333;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 10px;
        }
    </style>
    <script>
        let ws = null;
        let reconnectAttempts = 0;
        const MAX_RECONNECT_ATTEMPTS = 5;
        const RECONNECT_DELAY = 1000;
        let sentLogs = new Set();

        function connect() {
            if (ws !== null) {
                ws.close();
            }

            ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onmessage = function(event) {
                const log = document.getElementById('log');
                const data = JSON.parse(event.data);
                
                if (!sentLogs.has(data.id)) {
                    sentLogs.add(data.id);
                    const entry = document.createElement('div');
                    entry.className = `log-entry ${data.level}`;
                    entry.innerHTML = `<strong>${data.timestamp}</strong> - ${data.level}: ${data.message}`;
                    log.appendChild(entry);
                    log.scrollTop = log.scrollHeight;
                }
            };
            
            ws.onclose = function() {
                if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    reconnectAttempts++;
                    setTimeout(connect, RECONNECT_DELAY * reconnectAttempts);
                } else {
                    console.error('WebSocket connection failed after maximum attempts');
                }
            };

            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };

            ws.onopen = function() {
                reconnectAttempts = 0;
                console.log('WebSocket connected successfully');
            };
        }

        // Iniciar conexión cuando se carga la página
        window.onload = connect;
    </script>
</head>
<body>
    <h1>Werchter Monitor</h1>
    <div id="log"></div>
</body>
</html>
"""