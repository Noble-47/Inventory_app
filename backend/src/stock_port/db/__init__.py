from stock_port.db.audit import AuditDB
from stock_port.db.orders import OrderDB
from stock_port.db.records import RecordDB
from stock_port.db.suppliers import SupplierDB
from stock_port.db.db import db_session, create_tables


class DB:

    def __enter__(self):
        self.session = next(db_session())
        self.prepare()
        return self

    def prepare(self):
        events = []
        self.sales = OrderDB(self.session, events)
        self.audit = AuditDB(self.session)
        self.records = RecordDB(self.session)
        self.orders = OrderDB(self.session, events=events)
        self.suppliers = SupplierDB(self.session)
        self.events = events

    def __exit__(self, *args, **kwargs):
        self.session.rollback()

    def commit(self):
        self.session.commit()
        for order in self.orders.seen:
            self.events.extend(order.events)

    def collect_events(self):
        for event in self.events:
            yield event
        self.events.clear()
