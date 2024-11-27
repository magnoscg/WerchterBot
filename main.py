import os
import uvicorn
from src.web.app import app
from src.config import DEFAULT_PORT

if __name__ == "__main__":
    port = int(os.getenv("PORT", DEFAULT_PORT))
    uvicorn.run(app, host="0.0.0.0", port=port)