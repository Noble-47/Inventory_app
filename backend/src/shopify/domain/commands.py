import uuid

from pydantic import BaseModel, Field


class Command(BaseModel, frozen=True):
    pass


class CreateAccount(Command):
    firstname: str
    lastname: str
    email: str
    password: str


class VerifyAccount(Command):
    verification_str: str


class CreateBusiness(Command):
    name: str
    email: str


class UpdateSetting(Command):
    entity_id: uuid.UUID
    name: str
    value: str


class AddShop(Command):
    business_id: uuid.UUID
    location: str


class RemoveShop(Command):
    business_id: uuid.UUID
    shop_id: uuid.UUID


class CreateAssignmentToken(Command):
    business_id: uuid.UUID
    shop_id: uuid.UUID
    email: str
    permissions: str | dict[str, list[str]] = Field(default="*")


class CreateManager(CreateAccount):
    email: str
    token_str: str


class AssignManager(Command):
    shop_id: uuid.UUID
    account_id: int


class DismissManager(Command):
    business_id: uuid.UUID
    shop_id: uuid.UUID
