from datetime import datetime
import uuid
import json

from pydantic import BaseModel, Field
from sqlalchemy import select

from inventory.domain import events


class StockLog(BaseModel):
    id: int | None = Field(default=None, serialization_alias="audit_id")
    shop_id: uuid.UUID
    sku: str
    action: str = Field(validation_alias="name")
    event_time: datetime
    description: str
    event_hash: str
    payload: str


class BatchLog(StockLog):
    id: int | None = Field(default=None, serialization_alias="audit_id")
    shop_id: uuid.UUID
    sku: str
    batch_ref: str
    action: str = Field(validation_alias="name")
    event_time: datetime
    description: str
    event_hash: str
    payload: str


class Audit:

    Model = None

    def __init__(self, session, events=None):
        self.session = session
        self.events = events or []

    def get(self, audit_id: int):
        audit = self.session.exec(select(Model).where(Model.id == audit_id)).first()
        return audit


class StockAudit(Audit):
    Model = StockLog

    def add(self, event: events.Event):
        serialized_event = event.serialize()
        serialized_event["payload"] = json.dumps(serialized_event["payload"])
        audit = StockLog(**serialized_event)
        self.session.add(audit)

    def fetch(self, shop_id: uuid.UUID, sku: str):
        audits = self.session.scalars(
            select(StockLog)
            .where(StockLog.sku == sku)
            .where(StockLog.shop_id == shop_id)
            .order_by(StockLog.event_time)
        ).all()
        return audits


class BatchAudit(Audit):
    Model = BatchLog

    def add(self, event: events.Event):
        serialized_event = event.serialize()
        serialized_event["payload"] = json.dumps(serialized_event["payload"])
        audit = BatchLog(**serialized_event)
        self.session.add(audit)

    def fetch_stock_log(self, sku: str):
        audits = self.session.exec(
            select(BatchLog).where(BatchLog.sku == sku).order_by(BatchLog.event_time)
        ).all()
        return audits

    def fetch(self, sku, shop_id, batch_ref: str):
        audits = self.session.scalars(
            select(BatchLog)
            .where(BatchLog.batch_ref == batch_ref)
            .where(BatchLog.sku == sku)
            .where(BatchLog.shop_id == shop_id)
            .order_by(BatchLog.event_time)
        ).all()
        return audits
