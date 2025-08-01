import json

from sqlmodel import Session, select

from stock_port.domain import events
from stock_port.domain.models import OrderAudit


class AuditDB:

    def __init__(self, session: Session, events=None):
        self.session = session
        self.events = events or []

    def add(self, event: events.Event):
        serialized_event = event.serialize()
        serialized_event["payload"] = event.json()["payload"]
        audit = OrderAudit(**serialized_event)
        self.session.add(audit)

    def get(self, audit_id: int, shop_id: str):
        audit = self.session.exec(
            select(OrderAudit).where(
                OrderAudit.id == audit_id, OrderAudit.shop_id == shop_id
            )
        ).first()
        return audit

    def fetch(self, shop_id: str):
        audits = self.session.exec(
            select(OrderAudit)
            .where(OrderAudit.shop_id == shop_id)
            .order_by(OrderAudit.time)
        ).all()
        return audits
