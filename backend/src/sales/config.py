from pathlib import Path
import os

from dotenv import load_dotenv

SERVICE_FOLDER = Path(__file__).parent
DATABASE_URL = f"sqlite:///{SERVICE_FOLDER / 'sales.db'}"
