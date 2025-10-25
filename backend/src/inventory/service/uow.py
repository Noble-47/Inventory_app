from typing import Deque

from inventory.adapters import repository
from inventory.adapters import products
from inventory.adapters import audit
from inventory import config

from inventory.adapters.orm import db_session
from inventory.adapters.inventory import InventoryDB


class UnitOfWork:

    def __enter__(self):
        # self.session = self.session_factory()
        self.prepare()
        return self

    def prepare(self):
        events = []
        self.session = next(db_session())
        self.stocks = repository.SQLStockRepository(session=self.session, events=events)
        self.stock_audit = audit.StockAudit(session=self.session)
        self.batch_audit = audit.BatchAudit(session=self.session)
        self.inventory = InventoryDB(session=self.session, events=events)
        self.products = products.Product(session=self.session)
        self.events = events

    def __exit__(self, *args, **kwargs):
        self.rollback()
        self.session.close()

    def commit(self):
        for stock in self.stocks.seen:
            self.events.extend(stock.events)
            stock.events.clear()
        self.session.commit()

    def rollback(self):
        # has no effect if self.commit is called
        # rolls back uncommited changes
        self.session.rollback()

    def collect_new_events(self):
        if not hasattr(self, "events"):
            return
        for event in self.events:
            yield event
        self.events.clear()
