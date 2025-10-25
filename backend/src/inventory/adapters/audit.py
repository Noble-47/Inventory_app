from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid
import json

from sqlalchemy import select

from inventory.domain import events


@dataclass
class StockLog:
    name: str
    shop_id: str
    sku: str
    event_time: datetime
    description: str
    event_hash: str
    payload: str
    id: int | None = field(default=None)

    def __post_init__(self):
        self.shop_id = str(self.shop_id)

    def model_dump(self):
        return asdict(self)


@dataclass
class BatchLog:
    name: str
    shop_id: str
    sku: str
    batch_ref: str
    event_time: datetime
    description: str
    event_hash: str
    payload: str
    id: int | None = field(default=None)

    def __post_init__(self):
        self.shop_id = str(self.shop_id)

    def model_dump(self):
        return asdict(self)


class Audit:

    Model = None

    def __init__(self, session, events=None):
        self.session = session
        self.events = events or []

    def add(self, event: events.Event):
        serialized_event = event.serialize()
        serialized_event["payload"] = json.dumps(serialized_event["payload"])
        audit = self.Model(**serialized_event)
        self.session.add(audit)

    def get(self, audit_id: int):
        audit = self.session.exec(select(Model).where(Model.id == audit_id)).first()
        return audit


class StockAudit(Audit):
    Model = StockLog

    def fetch(self, shop_id: uuid.UUID, sku: str):
        shop_id = str(shop_id)
        audits = self.session.scalars(
            select(StockLog)
            .where(StockLog.sku == sku)
            .where(StockLog.shop_id == shop_id)
            .order_by(StockLog.event_time)
        ).all()
        return audits


class BatchAudit(Audit):
    Model = BatchLog

    def fetch_stock_log(self, sku: str):
        audits = self.session.exec(
            select(BatchLog).where(BatchLog.sku == sku).order_by(BatchLog.event_time)
        ).all()
        return audits

    def fetch(self, sku, shop_id, batch_ref: str):
        shop_id = str(shop_id)
        audits = self.session.scalars(
            select(BatchLog)
            .where(BatchLog.batch_ref == batch_ref)
            .where(BatchLog.sku == sku)
            .where(BatchLog.shop_id == shop_id)
            .order_by(BatchLog.event_time)
        ).all()
        return audits
