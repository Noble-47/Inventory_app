from pathlib import Path
import os

from dotenv import load_dotenv

SERVICE_DIR = Path(__file__).parent

DATABASE_PATH = os.environ.get("TRACK_DATABASE_PATH", SERVICE_DIR / "tracker.db")


def get_database_url():
    return f"sqlite:///{DATABASE_PATH}"
