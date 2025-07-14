from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from inventory.domain.read_models import StockView as Stock


class View:

    def __init__(self, session):
        self.session = session

    def add_stock_to_inventory(self, shop_id, sku, level, name, batch_ref, price):
        stock = Stock(sku=sku, shop_id=shop_id, name=name, level=level)
        self.session.add(Stock)

    def delete_stock_from_inventory(self, shop_id, sku):
        stock = self.session.execute(
            select(Stock).where(Stock.shop_id == shop_id, Stock.sku == sku)
        ).first()
        if stock:
            self.session.delete(stock)

    def add_batch(self, shop_id, sku, ref, price, stock_in_units, stock_time):
        batch = Batch(
            shop_id=shop_id,
            sku=sku,
            ref=ref,
            price=price,
            stock_in_units=stock_in_units,
            stock_time=stock_time,
        )
        self.session.add(batch)

    def dispatch_batch(self, shop_id, sku, batch_ref, price, dispatched_quantity):
        batch = self.session.execute(
            select(Batch).where(
                Batch.ref == batch_ref, Batch.shop_id == shop_id, Batch.sku == sku
            )
        ).first()
        if batch is None or stock is None:
            return
        batch.quantity -= dispatched_quantity

    def update_batch_price(self, batch_ref, price):
        batch = self.session.execute(
            select(Batch).where(Batch.ref == batch_ref)
        ).first()
        if batch:
            batch.price = price

    def update_batch_quantity(self, shop_id, sku, batch_ref, quantity):
        batch = self.session.execute(
            select(Batch).where(Batch.ref == batch_ref)
        ).first()

        stock = self.session.execute(
            select(Stock).where(Stock.sku == sku, Stock.shop_id == shop_id)
        ).first()

        if batch:
            batch.quantity = quantity
