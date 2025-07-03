from pathlib import Path
import pytz
import os

from dotenv import load_dotenv

load_dotenv()

INVENTORY_DIR = Path(__file__).parent
SETTINGS_PATH = INVENTORY_DIR / os.environ.get("SETTINGS_PATH", "settings.db")
TIMEZONE = pytz.timezone("Africa/Lagos")
DATABASE_URL = os.environ.get(
    "DATABASE_URL", f"sqlite:///{INVENTORY_DIR / 'inventory.db'}"
)


def get_database_url():
    return INVENTORY_DIR / os.environ.get("DATABASE", "inventory.db")
