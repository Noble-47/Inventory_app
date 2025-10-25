from contextlib import contextmanager
from datetime import datetime
import json

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event, func, select

from shared import TIMEZONE
from stock_port import config
from stock_port.domain.models import (
    Order,
    Supplier,
    Record,
    BatchLine,
    BaseModel,
    ShopSupplier,
    OrderAudit,
)

engine = create_engine(config.DATABASE_URL)


def create_tables():
    BaseModel.metadata.create_all(engine)


def db_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


@event.listens_for(Supplier, "before_insert")
def receive_before_insert(mapper, connection, target):
    # Get the current max counter value and increment it
    max_id = connection.execute(select(func.max(Supplier.id))).scalar()
    print(max_id)
    target.id = (max_id or 0) + 1


@event.listens_for(OrderAudit, "load")
def load_audit_payload(target, context):
    payload = json.loads(target.payload)
    if "expected_delivery_date" in payload:
        payload["expected_delivery_date"] = datetime.fromtimestamp(
            payload["expected_delivery_date"], TIMEZONE
        )
    if "delivery_date" in payload:
        payload["delivery_date"] = datetime.fromtimestamp(
            payload["delivery_date"], TIMEZONE
        )
    target.payload = payload
