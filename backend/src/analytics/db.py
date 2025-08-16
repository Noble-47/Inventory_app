from sqlmodel import create_engine

from analytics.models import AnalyticModels, Inventory, Sale, Order, Debt, Analytics
from analytics import config

engine = create_engine(config.DATABASE_URL)


def create_tables():
    AnalyticModels.metadata.create_all(engine)
