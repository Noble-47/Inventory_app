from datetime import datetime
import uuid
import json

from pydantic import BaseModel, Field

from inventory.domain import events

class StockLog(BaseModel):
    id : int | None = Field(default=None)
    shop_id: uuid.UUID
    sku: str
    time : datetime
    description : str
    event_hash : str
    payload : str


class BatchLog(BaseModel):
    id : int | None = Field(default=None)
    sku: str
    shop_id: uuid.UUID
    batch_ref: str
    time : datetime
    description : str
    event_hash : str
    payload : str


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
        audit = self.session.exec(
            select(Model).where(
                Model.id == audit_id
            )
        ).first()
        return audit


class ShopAudit:

    def fetch(self, shop_id: uuid.UUID):
        audits = self.session.exec(
            select(StockLog)
            .where(StockLog.shop_id == shop_id)
            .order_by(StockLog.time)
        ).all()
        return audits


class StockAudit(Audit):
    Model = StockLog

    def fetch(self, shop_id: uuid.UUID, sku:str):
        audits = self.session.exec(
            select(StockLog)
            .where(StockLog.sku == sku)
            .where(StockLog.shop_id == shop_id)
            .order_by(StockLog.time)
        ).all()
        return audits


class BatchAudit(Audit):
    Model = BatchLog

    def fetch_stock_log(self, sku:str):
        audits = self.session.exec(
            select(BatchLog)
            .where(BatchLog.sku == sku)
            .order_by(BatchLog.time)
        ).all()
        return audits


    def fetch(self, batch_ref:str):
        audits = self.session.exec(
            select(BatchLog)
            .where(BatchLog.batch_ref == batch_ref)
            .where(BatchLog.sku == sku)
            .where(BatchLog.shop_id == shop_id)
            .order_by(BatchLog.time)
        ).all()
        return audits


