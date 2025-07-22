from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

parent_dir = Path(__file__).parent

database_url = os.environ.get(
    "EXCHANGE_DATABASE_URL", f"sqlite:///{parent_dir / 'exchange.db'}"
)
root_url = os.environ.get("EXCHANGE_URL", f"http://localhost:8080/exchange")
