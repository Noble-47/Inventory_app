import uuid
import json

from sqlmodel import Session, select

from shopify.domain import events
from shopify.db.models import AuditLog


class Audit:

    def __init__(self, session: Session, events=None):
        self.session = session
        self.events = events or []

    def add(self, event: events.Event):
        serialized_event = event.serialize()
        serialized_event['payload'] = json.dumps(serialized_event['payload'])
        audit = AuditLog(**serialized_event)
        self.session.add(audit)

    def get(self, audit_id: int, business_id: uuid.UUID):
        audit = self.session.exec(
            select(AuditLog).where(
                AuditLog.id == audit_id, AuditLog.business_id == business_id
            )
        ).first()
        return audit

    def fetch(self, business_id: uuid.UUID):
        audits = self.session.exec(
            select(AuditLog)
            .where(AuditLog.business_id == business_id)
            .order_by(AuditLog.time)
        ).all()
        return audits
