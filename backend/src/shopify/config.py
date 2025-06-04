from pathlib import Path
import os

from dotenv import load_dotenv
import pytz

load_dotenv()

SERVICE_DIR = Path(__file__).parent

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{SERVICE_DIR / 'shopify.db'}")

TIMEZONE = pytz.timezone("Africa/Lagos")

INVITE_TOKEN_EXPIRATION_SECONDS = 1 * 24 * 60 * 60  # 1 day
VERIFICATION_TOKEN_EXPIRATION_SECONDS = 3 * 24 * 60 * 60  # 3 days
API_TOKEN_EXPIRATION_SECONDS = 1 * 24 * 60 * 60  # 1 day

SECRET_KEY = os.environ.get("SECRET_KEY", "SECRET_KEY")

TOKEN_ALGORITHM = os.environ.get("TOKEN_ALGORITHM", "HS256")

ALLOWED_ORIGINS = ["*"]

DEFAULT_SETTINGS = [
    {
        "name": "CONTROL STRATEGY",
        "tag": "inventory",
        "description": "Defines the method used for computing inventory value (options : [FIFO, LIFO, WeightedAverage])",
        "default": "FIFO",
    },
    {
        "name": "LOW LEVEL",
        "tag": "inventory",
        "description": "Defines the level of stock that should be flaged as low stock",
        "default": 10,
    },
]
