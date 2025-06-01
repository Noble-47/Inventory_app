from pathlib import Path
import pytz
import os

from dotenv import load_dotenv

load_dotenv()

INVENTORY_DIR = Path(__file__).parent
SETTINGS_PATH = INVENTORY_DIR / os.environ.get("SETTINGS_PATH", "settings.db")
TIMEZONE = pytz.timezone('Africa/Lagos')

def get_database_url():
    return INVENTORY_DIR / os.environ.get("DATABASE", "inventory.db")


