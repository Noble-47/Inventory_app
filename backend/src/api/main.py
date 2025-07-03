from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from api import shopify
from api import inventory
from api import stock_port

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
inventory.setup(app)
stock_port.setup(app)
