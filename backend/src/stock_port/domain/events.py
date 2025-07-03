from datetime import datetime
from uuid import UUID
import hashlib

from pydantic import BaseModel

from shared import datetime_now_func


class Event(BaseModel):

    name: str = Field(default=self.__class__.__name__)
    time: datetime = Field(default_factory(datetime_now_func))

    @property
    def event_hash(self):
        attrs = list(
            str(v) for k, v in asdict(self) if k not in ["time", "description"]
        )
        raw = "|".join(attrs).encode()
        return hashlib.sha256(raw).hexdigest()

    @property
    def payload(self):
        return asdict(self)

    def serialize(self):
        return {
            "name": self.name,
            "order_id": self.order_id,
            "description": self.description,
            "payload": self.payload,
            "event_hash": self.event_hash,
            "time": self.time,
        }


class OrderCreated(Event):
    pass


class OrderCancelled(Event):
    pass


class OrderDelivered(Event):
    pass
