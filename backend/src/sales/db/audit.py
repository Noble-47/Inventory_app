import uuid
import json

from sqlmodel import Session, select

from sales.domain import events
from sales.domain.models import SaleAudit


class AuditDB:

    def __init__(self, session: Session, events=None):
        self.session = session
        self.events = events or []

    def add(self, event: events.Event):
        serialized_event = event.serialize()
        serialized_event["payload"] = json.dumps(serialized_event["payload"])
        audit = SaleAudit(**serialized_event)
        self.session.add(audit)

    def get(self, audit_id: int, shop_id: uuid.UUID):
        audit = self.session.exec(
            select(SaleAudit).where(
                SaleAudit.id == audit_id, SaleAudit.shop_id == shop_id
            )
        ).first()
        return audit

    def fetch(self, shop_id: uuid.UUID):
        audits = self.session.exec(
            select(SaleAudit)
            .where(SaleAudit.shop_id == shop_id)
            .order_by(SaleAudit.time)
        ).all()
        return audits
