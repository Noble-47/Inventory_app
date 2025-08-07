from typing import Annotated, Optional
from datetime import datetime
from uuid import UUID
import hashlib

from pydantic import BaseModel, Field, PlainSerializer

from shared import datetime_now_func

SerializableUUID = Annotated[
    UUID, PlainSerializer(lambda uid: str(uid), return_type=str)
]


SerializableDateTime = Annotated[
    datetime, PlainSerializer(lambda d: d.timestamp(), return_type=float)
]

StringSerializedDict = Annotated[
    dict, PlainSerializer(lambda data: json.dumps(data), return_type=str)
]


class Event(BaseModel):
    event_time: SerializableDateTime = Field(default_factory=datetime_now_func)

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
        model_dump.pop("shop_id")
        model_dump.pop("sale_ref")
        model_dump.pop("event_time")
        return model_dump

    def serialize(self):
        return {
            "name": self.__class__.__name__,
            "ref": self.sale_ref,
            "shop_id": self.shop_id,
            "event_hash": self.event_hash,
            "time": self.event_time.timestamp(),
            "description": self.description,
            "payload": self.payload,
        }


class Unit(BaseModel):
    sku: str = Field(validation_alias="product_sku")
    quantity: int
    price_at_sale: float


class NewSaleAdded(Event):
    shop_id: SerializableUUID
    sale_ref: SerializableUUID
    selling_price: float
    amount_paid: float
    firstname: str
    lastname: str
    customer_phone: str
    products: list[Unit]
    description: str = Field(default="New sale record added")


class Updates(BaseModel):
    phone: str | None = Field(default=None)
    firstname: str | None = Field(default=None)
    lastname: str | None = Field(default=None)
    # products: list[StringSerializedDict] | None = Field(default=None)


class SaleRecordUpdated(Event):
    shop_id: SerializableUUID
    sale_ref: SerializableUUID
    firstname: str
    lastname: str
    customer_phone: str
    selling_price: float | None = Field(default=None)
    amount_paid: float | None = Field(default=None)
    description: str = Field(default="Sale record updated")


class SaleRecordDeleted(Event):
    shop_id: SerializableUUID
    sale_ref: SerializableUUID
    description: str = Field(default="Sale record deleted")


class CustomerRecordUpdated(Event):
    shop_id: SerializableUUID
    sale_ref: Optional[SerializableUUID] = Field(default=None)
    firstname: str
    lastname: str
    phone: str
    new_phone: str | None = Field(default=None)
