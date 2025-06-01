from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy import and_

from inventory.domain.models import Stock, Batch


class StockRepository(ABC):

    @abstractmethod
    def get(self, sku: str):
        pass

    @abstractmethod
    def get_only_dispatchable_batches(self, sku: str):
        pass

    @abstractmethod
    def add(stock: Stock):
        pass

    @abstractmethod
    def __len__(self):
        pass


class SQLStockRepository(StockRepository):

    def __init__(self, session: Session):
        self.session = session
        self.seen = set()

    def __len__(self):
        return self.session.scalars(select(func.count()).select_from(Stock)).one()

    def get_only_dispatchable_batches(self, sku: str):
        batches = self.session.scalars(
            select(Batch).where(and_(Batch.sku == sku, Batch.quantity > 0))
        ).all()
        stock = self.session.scalars(select(Stock).where(Stock.sku == sku)).one()
        stock.batches = batches
        self.seen.add(stock)
        return stock

    def get(self, sku: str):
        stmt = select(Stock).where(Stock.sku == sku)
        stock = self.session.scalars(stmt).one()
        self.seen.add(stock)
        return stock

    def add(self, stock: Stock):
        self.seen.add(stock)
        self.session.add(Stock)
