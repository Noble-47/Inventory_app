from sales.db.sales import SalesDB
from sales.db.audit import AuditDB
from sales.db.customers import CustomersDB
from sales.db.records import RecordsDB
from sales.db.db import db_session, create_tables

class DB:

    def __enter__(self):
        self.session = next(db_session())
        self.prepare()
        return self

    def prepare(self):
        events = []
        self.customers = CustomersDB(self.session)
        self.sales = SalesDB(self.session, events)
        self.audit = AuditDB(self.session)
        self.record = RecordsDB(self.session)
        self.events = events

    def __exit__(self, *args, **kwargs):
        self.session.rollback()

    def commit(self):
        self.session.commit()

    def collect_events(self):
        for event in self.events:
            yield event
        self.events.clear()



__all__ = [DB, AuditDB, SalesDB, CustomersDB, db_session, create_tables]
