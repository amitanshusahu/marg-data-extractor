# log_setup.py
from pathlib import Path
import os
import logging
from logging.handlers import RotatingFileHandler

APP_DATA_DIR = Path(os.getenv("LOCALAPPDATA", os.getcwd())) / "NexInsights"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

LOGS_DIR = APP_DATA_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "app.log"

logger = logging.getLogger("NexInsights")
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Optional: also log to console
# console = logging.StreamHandler()
# console.setFormatter(formatter)
# logger.addHandler(console)
# well this is super cool log for developer better than print, well i tried it myself 
# but we have a problem print is less cognitive load
# and look at me writing this stupid doc..T_T