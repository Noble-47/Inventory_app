from contextlib import contextmanager
import json

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

from sales import config
from sales.domain.models import (
    SalesModel,
    Sale,
    Product,
    SaleProductLink,
    Customer,
    SaleAudit,
)

engine = create_engine(config.DATABASE_URL)


def create_tables():
    SalesModel.metadata.create_all(engine)


def db_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


@event.listens_for(SaleAudit, "load")
def load_payload(audit, context):
    audit.payload = json.loads(audit.payload)
    return audit
