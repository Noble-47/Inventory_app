from typing import Any, Annotated

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from exchange.channels import inventory
from exchange.channels import analytics
from exchange.channels import tracker
from exchange.channels import shopify
from exchange.channels import orders
from exchange.channels import sales

from exchange.router import Router
from exchange.models import Message
from exchange.hub import Hub, publish
from shared import get_rotating_logger
from exchange.db import create_tables, start_mappers, db_session

logger = get_rotating_logger("exchange", "exchange.log")

exchange_app = FastAPI(title="Inventra Exchange")

exchange_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http:127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@exchange_app.on_event("startup")
def startup():
    start_mappers()
    create_tables()


def create_hub(session):
    router = Router(session)
    hub = Hub(router)

    inventory.initialize_hub(hub)
    analytics.initialize_hub(hub)
    tracker.initialize_hub(hub)
    shopify.initialize_hub(hub)
    orders.initialize_hub(hub)
    sales.initialize_hub(hub)

    hub.begin()
    return hub


def setup(app: FastAPI):
    # exchange primer
    publish("dummy-notification", "dummy-subject", {"dummy": "data"})
    publish("dummy-notification", "dummy-subject", {"dummy": "data"})
    publish("dummy-notification", "dummy-subject", {"dummy": "data"})


@exchange_app.post("/exchange/{channel}/{subject}")
async def post_message(
    channel: str,
    subject: str,
    message: dict[str, Any],
    session: Annotated[Session, Depends(db_session)],
):
    hub = create_hub(session)
    logger.info(f"[o] Received Message From - {channel}")
    logger.info(f"[-] Message - {subject}")
    message = Message(subject=subject, data=message)
    await hub.push(message)
    return "Message Acknowledged"
