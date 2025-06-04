from sqlmodel import SQLModel, create_engine, Session
from datetime import datetime, timedelta
from sqlalchemy import event, text

from shopify import config
from shopify.domain.read_models import BusinessView, ShopView
from shopify.domain.models import Account, Business, BusinessRegistry, ShopRegistry
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

    def get(self, *args, **kwargs):
        obj = self._get(*args, **kwargs)
        return obj

    def create(self, *args, **kwargs):
        obj = self._create(*args, **kwargs)
        self.session.add(obj)
        return obj

@event.listens_for(Token, "load")
def check_token_has_expired(target, context):
    token = target
    time_lived = (token.created - datetime.now(config.TIMEZONE)).seconds
    if time_lived >= token.ttl:
        token.expired = True
        token.is_valid = False
    return token


def create_default_settings(engine):
    with engine.connect() as conn:
        conn.execute(text(
            """
            INSERT INTO setting (name, tag, description)
            VALUES (:name, :tag, :description)
            ON CONFLICT(name)
            DO NOTHING
            """
        ), config.DEFAULT_SETTINGS)
        conn.commit()

engine = create_engine(config.DATABASE_URL)

def create_tables():
    SQLModel.metadata.create_all(engine)
    create_default_settings(engine)

def db_session():
    with Session(engine) as session:
        yield session
