from typing import Deque

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from inventory.adapters import views
from inventory import config

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(f"sqlite+pysqlite:///" + config.DATABASE_URL)
)


class UnitOfWork:

    def __init__(self, message_queue: Deque, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.stocks = repository.SQLStockRepository(self.session)
        self.views = views.View(self.session)
        self.events = []
        return self

    def __exit__(self):
        self.rollback()
        self.session.close()

    def commit(self):
        for stock in self.stock.seen:
            self.events.extend(stock.events)
            stock.events.clear()
        self.session.commit()

    def rollback(self):
        # has no effect if self.commit is called
        # rolls back uncommited changes
        self.session.rollback()

    def collect_new_events(self):
        for event in self.events:
            yield event
        self.events.clear()
