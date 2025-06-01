from sqlmodel import SQLModel, create_engine, Session
from datetime import datetime, timedelta
from sqlalchemy import event

from shopify import config
from shopify.domain.read_models import BusinessView, ShopView
from shopify.domain.models import Account, Business, Shop, Registry
from shopify.db.models import (
    Token,
    AccountVerification,
    AuditLog,
    Setting,
    EntitySetting,
)


class BaseRepo:
    def __init__(self, session: Session, events: list = []):
        self.session = session
        self.events = events

    def get(*args, **kwargs):
        obj = self._get(*args, **kwargs)
        self.session.add(obj)
        return obj

    def create(*args, **kwargs):
        obj = self._create(*args, **kwargs)
        self.session.add(obj)
        return obj

    # def save(self, obj: ORMObject):
    #    self.session.add(obj)
    #    self.session.refresh(obj)
    #    return obj


@event.listens_for(Token, "load")
def check_token_has_expired(mapper, connection, target) -> Token:
    token = target
    time_lived = (token.created - datetime.now(config.TIMEZONE)).seconds
    if time_lived >= token.ttl:
        token.expired = True
        token.is_valid = False
    return token


def create_tables(database_url=config.DATABASE_URL):
    engine = create_engine(database_url)
    SQLModel.metadata.create_all(engine)


def db_session():
    with Session(engine) as session:
        yield session
