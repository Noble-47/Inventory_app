from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy import and_

from shared import datetime_now_func

from inventory.domain.models import Stock, Batch, manual_batch_ref_generator
from inventory.exceptions import StockNotFound
from inventory.domain import events


class SQLStockRepository:

    def __init__(self, session: Session, events: list = list()):
        self.session = session
        self.seen = set()
        self.events = events

    def __len__(self):
        return self.session.scalars(select(func.count()).select_from(Stock)).one()

    def get_only_dispatchable_batches(self, shop_id: str, sku: str):
        batches = self.session.scalars(
            select(Batch).where(and_(Batch.sku == sku, Batch.quantity > 0))
        ).all()
        stock = self.session.scalars(
            select(Stock).where(Stock.shop_id == shop_id, Stock.sku == sku)
        ).one()
        stock.batches = batches
        self.seen.add(stock)
        return stock

    def get(self, shop_id: UUID, sku: str):
        stmt = select(Stock).where(Stock.sku == sku, Stock.shop_id == shop_id)
        stock = self.session.scalars(stmt).first()
        if stock is None:
            raise StockNotFound()
        self.seen.add(stock)
        return stock

    def create(self, sku: str, name: str, shop_id: UUID, quantity: int, price: float):
        time = datetime_now_func()
        stock = Stock(sku=sku, name=name, shop_id=shop_id)
        ref = manual_batch_ref_generator()
        self.events.append(
            events.StockCreated(sku=sku, shop_id=shop_id, product=name, level=quantity)
        )
        stock.add(quantity=quantity, ref=ref, price=price, time=time)
        self.session.add(stock)
        self.seen.add(stock)
        return stock

    def delete(self, sku: str, shop_id: UUID):
        stock = self.get(sku=sku, shop_id=shop_id)
        self.session.delete(stock)
        self.events.append(events.StockDeleted(sku=sku, shop_id=shop_id))

    def check_exists(self, sku: str, shop_id: UUID):
        stock_id = self.session.execute(
            select(Stock.sku).where(Stock.sku == sku, Stock.shop_id == shop_id)
        ).first()
        return True if stock_id else False
