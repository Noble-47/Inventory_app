from sales.db import listners

from sales.db.sales import SalesDB
from sales.db.audit import AuditDB
from sales.db.customers import CustomersDB
from sales.db.db import db_session, create_tables

class DB:

    def __enter__(self):
        self.session = next(self.db_session())
        self.prepare()
        self.listners = self.inject_db_listners()
        return self

    def prepare(self):
        events = []
        self.customers = CustomerDB(session)
        self.sales = SalesDB(session, events)
        self.audit = AuditDB(session)
        self.events = events

    def __exit__(self, *args, **kwargs):
        self.session.rollback()

    def commit(self):
        self.session.commit()
        self.handler_events()

    def collect_events(self):
        for event in self.events:
            yield event
        self.events.clear()

    def handle_events(self):
        for event in self.events:
            self.audit.add(event)
            listners.handle(event)


__all__ = [DB, AuditDB, SalesDB, CustomersDB, db_session, create_tables]
