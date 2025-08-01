import json
import hashlib
from datetime import datetime
from pydantic import BaseModel, Field

from shared import datetime_now_func, TIMEZONE


class Event(BaseModel):
    event_time: datetime = Field(default_factory=datetime_now_func)

    @property
    def event_hash(self):
        attrs = list(
            str(v)
            for k, v in self.model_dump().items()
            if (k not in ["description", "time"])
        )
        raw = "|".join(attrs).encode()
        return hashlib.sha256(raw).hexdigest()

    @property
    def payload(self):
        model_dump = self.model_dump()
        model_dump.pop("description")
        model_dump.pop("event_time")
        model_dump.pop("firstname")
        model_dump.pop("lastname")
        model_dump.pop("phone")
        model_dump.pop("sale_ref")
        return model_dump

    def serialize(self):
        return {
            "name": self.__class__.__name__,
            "shop_id": self.shop_id,
            "sale_ref": self.sale_ref,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "phone": self.phone,
            "event_hash": self.event_hash,
            "time": self.event_time,
            "description": self.description,
            "payload": self.payload,
        }

    def json(self):
        data = self.serialize()
        data["time"] = data["time"].timestamp()
        for key, value in data["payload"].items():
            if isinstance(value, datetime):
                data["payload"][key] = value.timestamp()
        data["payload"] = json.dumps(data["payload"])
        return data


class NewDebt(Event):
    shop_id: str
    firstname: str
    lastname: str
    phone: str
    sale_ref: str
    selling_price: float
    amount_paid: float
    description: str = Field(default="New debt record")


class PaymentReceived(Event):
    shop_id: str
    phone: str
    firstname: str
    lastname: str
    sale_ref: str
    amount_paid: float
    description: str = Field(default="Payment received")


class DebtCleared(Event):
    shop_id: str
    phone: str
    firstname: str
    lastname: str
    sale_ref: str
    reason: str
    description: str = Field(default="Debt cleared")
