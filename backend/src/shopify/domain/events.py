from functools import partial
from datetime import datetime
from typing import Annotated
import hashlib
import uuid

from pydantic import BaseModel, Field, PlainSerializer

from shopify.config import TIMEZONE


datetime_now_utc = partial(datetime.now, tz=TIMEZONE)
SerializableUUID = Annotated[
    uuid.UUID, PlainSerializer(lambda uid: str(uid), return_type=str)
]


def camel_case_split(s):
    modified_string = list(map(lambda x: "_" + x if x.isupper() else x, s))
    split_string = "".join(modified_string).split("_")
    split_string = list(filter(lambda x: x != "", split_string))
    return " ".join(split_string)


class Event(BaseModel):
    event_time: datetime = Field(default_factory=datetime_now_utc)

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
        model_dump.pop("event_time")
        return model_dump

    def serialize(self):
        return {
            "name": self.__class__.__name__,
            "business_id": self.business_id,
            "event_hash": self.event_hash,
            "time": self.event_time.timestamp(),
            "description": self.description,
            "payload": self.payload,
        }


class NewBusinessCreated(Event):
    business_id: SerializableUUID
    name: str
    owner_name: str
    owner_email: str
    description: str = Field(default="Created Business.")


class AddedNewShop(Event):
    business_id: SerializableUUID
    shop_id: SerializableUUID
    shop_location: str
    description: str = Field(default="Added New Shop To Business")


class RemovedShop(Event):
    business_id: SerializableUUID
    location: str
    description: str = Field(default="Deleted Shop From Business")


class AssignedNewManager(Event):
    business_id: SerializableUUID
    shop_id: SerializableUUID
    manager_email: str
    shop_location: str
    manager_name: str
    description: str = Field(default="Assigned Shop Manager")


class DismissedManager(Event):
    business_id: SerializableUUID
    shop_id: SerializableUUID
    shop_location: str
    description: str = Field(default="Dismissed Shop Manager")


class CreatedManagerInviteToken(Event):
    business_id: SerializableUUID
    shop_id: SerializableUUID
    shop_location: str
    email: str
    token_str: str
    description: str = Field(default="Created Manager Invite")
