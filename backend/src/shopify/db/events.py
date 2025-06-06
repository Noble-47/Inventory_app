import uuid

from pydantic import Field

from shopify.domain.events import Event, datetime_now_utc


class Event(Event):
    # event_time = Field(default_factory=datetime_now_utc)

    @property
    def payload(self):
        return self.model_dump()


class VerificationTokenCreated(Event):
    email: str
    verification_str: str


class NewAccountCreated(Event):
    firstname: str
    lastname: str
    email: str


class AccountVerified(Event):
    email: str
    firstname: str
    lastname: str


class SettingUpdated(Event):
    tag: str
    entity_id: uuid.UUID
    entity_type: str
    value: str | int
