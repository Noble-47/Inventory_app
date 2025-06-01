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
API_TOKEN_EXPIRATION_SECONDS = 1 * 60  # 1 hour
