from pathlib import Path
import pytz
import os

from dotenv import load_dotenv

load_dotenv()

INVENTORY_DIR = Path(__file__).parent
TIMEZONE = pytz.timezone("Africa/Lagos")
DATABASE_URL = os.environ.get("DATABASE_URL", INVENTORY_DIR / "inventory.db")

DEFAULT_SETTINGS = [("control strategy", "fifo"), ("low level", "10")]


def get_database_url():
    return f"sqlite:///{DATABASE_URL}"


def get_async_url():
    return f"sqlite+aiosqlite:///{DATABASE_URL}"
