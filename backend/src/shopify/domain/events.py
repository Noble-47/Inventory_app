from functools import partial
from datetime import datetime
import hashlib
import uuid

from pydantic import BaseModel, Field

from shopify.config import TIMEZONE


datetime_now_utc = partial(datetime.now, tz=TIMEZONE)


class Event(BaseModel):
    event_time: datetime = Field(defualt_factory=datetime_now_utc)

    def model_post_init(self):
        self.time = datetime_now_utc().timestamp()

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
        model_dump.pop("business_id")
        return model_dump

    def serialize(self):
        return {
            "name": self.__class__.__name__,
            "business_id" : self.business_id,
            "event_hash": self.event_hash(),
            "time": self.time,
            "description": self.description,
            "payload": self.payload,
        }


class AddedNewShop(Event):
    business_id: uuid.UUID
    shop_id: uuid.UUID
    location: str
    description: str = "Added new shop to business"


class RemovedShop(Event):
    business_id: uuid.UUID
    location: str


class AssignedNewManager(Event):
    business_id: uuid.UUID
    shop_id: uuid.UUID
    manager_id: int
    description: str = "Assigned shop manager"


class DismissedManager(Event):
    business_id: uuid.UUID
    shop_ud: uuid.UUID
    account_id: int
    description: str = "Dismissed shop manager"


class CreatedManagerInviteToken(Event):
    business_id: uuid.UUID
    shop_id: uuid.UUID
    email: str
    token_str: str
