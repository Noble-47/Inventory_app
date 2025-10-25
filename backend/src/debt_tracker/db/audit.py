import uuid
import json

from sqlmodel import Session, select

from debt_tracker.domain import events
from debt_tracker.domain.models import DebtLog


class AuditDB:

    def __init__(self, session: Session, events=None):
        self.session = session
        self.events = events or []

    def add(self, event: events.Event):
        serialized_event = event.serialize()
        serialized_event["payload"] = json.dumps(serialized_event["payload"])
        audit = DebtLog(**serialized_event)
        self.session.add(audit)

    def get(self, audit_id: int):
        audit = self.session.exec(select(DebtLog).where(DebtLog.id == audit_id)).first()
        return audit

    def fetch(self, shop_id: uuid.UUID):
        audits = self.session.exec(
            select(DebtLog).where(DebtLog.shop_id == shop_id).order_by(DebtLog.time)
        ).all()
        return audits
