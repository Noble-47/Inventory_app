from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from api import sales
from api import shopify
from api import inventory
from api import analytics
from api import stock_port
from api import debt_tracker
from exchange import server as exchange_server

app = FastAPI(title="Inventra API")
ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

shopify.setup(app)

sales.setup(app)
inventory.setup(app)
analytics.setup(app)
stock_port.setup(app)
debt_tracker.setup(app)
exchange_server.setup(app)
