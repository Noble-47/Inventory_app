from shopify.domain.events import Event


class Event(Event):

    @property
    def payload(self):
        return self.model_dump()


class CreatedAccountVerificationToken(Event):
    email: str
    verification_str: str


class NewAccountCreated(Event):
    account_id: int
    firstname: str
    lastname: str
    email: str


class AccountVerified(Event):
    email: str
    firstname: str
    lastname: str

class SettingUpdated(Event):
    tag : str
    entity_id : str
    entity_type : str
    value : str | int
