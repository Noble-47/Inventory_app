import uuid

from sqlmodel import SQLModel


class ManagerInvites(SQLModel, table=False):
    email: str
    shop_id: uuid.UUID
    location: uuid.UUID
    accepted: bool
    date_accepted: datetime


class History(SQLModel, table=False):
    name: str
    description: str


class ShopSetting(SQLModel, table=False):
    name: str
    value: str | int


class Setting(SQLModel, table=False):
    name: str
    value: str | int
    shops: list[ShopSetting]
