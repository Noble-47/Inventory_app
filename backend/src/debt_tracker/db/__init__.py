from debt_tracker.db.debts import DebtDB
from debt_tracker.db.audit import AuditDB
from debt_tracker.db.debtors import DebtorDB
from debt_tracker.db.records import RecordsDB
from debt_tracker.db.db import db_session, create_tables


class DB:

    def __enter__(self):
        self.session = next(db_session())
        self.prepare()
        return self

    def prepare(self):
        events = []
        self.debts = DebtDB(self.session, events)
        self.debtors = DebtorDB(self.session, events)
        self.audit = AuditDB(self.session)
        self.records = RecordsDB(self.session)
        self.events = events

    def __exit__(self, *args, **kwargs):
        self.session.rollback()
        self.session.close()

    def commit(self):
        for debt in self.debts.seen:
            self.events.extend(debt.events)
        self.session.commit()

    def collect_events(self):
        if not hasattr(self, "events"):
            return []
        for event in sorted(self.events, key=lambda event: event.event_time):
            yield event
        self.events.clear()


__all__ = [DB, AuditDB, DebtDB, DebtorDB, db_session, create_tables]
