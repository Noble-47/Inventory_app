from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy import and_

from inventory.domain.models import Stock, Batch, global_stock_generator


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

    def create(self, global_sku:str, name:str, shop_id:uuid.UUID, quantity:int):
        stock = Stock(global_sku=global_sku, name=name, shop_id=shop_id, quantity=quantity)
        self.session.add(stock)
        return stock

    def check_exists(self, global_sku:str):
        stock_id = self.session.execute(select(Stock.id).where(Stock.global_sku == global_sku)).first()
        if stock_id return True else False
