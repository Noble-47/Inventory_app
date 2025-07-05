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

class OrderLine(BaseModel):
    sku:str
    ref:str
    cost:float

class NewOrderLine(OrderLine):
    expected_quantity:int

class OrderCreated(Event):
    shop_id:UUID
    order_id:UUID
    status:str
    supplier:str
    supplier_phone:str
    order_line:list[NewOrderLine]
    expected_delivery_date:datetime
    description:str = Field(default="New Order created")

class OrderCancelled(Event):
    order_id:UUID
    shop_id:UUID
    reason:str = Field(default="None given")
    description:str = Field(default="Order cancelled")

class CompletedOrderLine(OrderLine):
    sku:str
    ref:str
    delivered_quantity:int
    cost:float

class OrderCompleted(Event):
    order_id:UUID
    shop_id:UUID
    order_line:list[CompletedOrderLine]
    delivery_date:datetime
    description:str = Field(default="Order marked as completed.")

class OrderUpdated(Event):
    order_id:UUID
    shop_id:UUID
    reason:str = Field(default="None given.")
    update:str
    description:str = Field(default="Order was updated.")
