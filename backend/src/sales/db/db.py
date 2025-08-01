from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.orm import sessionmaker

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
