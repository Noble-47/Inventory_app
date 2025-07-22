from sqlmodel import create_engine, Session

from debt_tracker.domain.models import Debt, Debtor, DebtLog, Record, BaseModel

from debt_tracker import config

engine = create_engine(config.get_database_url())


def create_tables():
    BaseModel.metadata.create_all(engine)


def db_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
