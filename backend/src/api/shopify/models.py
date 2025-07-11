from typing import Union, Optional
from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Account(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    account_type: str | None = Field(default=None)


class AccountCreate(Account):
    password: str


class ShopDetail(BaseModel):
    id: uuid.UUID
    location: str
    manager: str | None = Field(default=None)


class BusinessDetail(BaseModel):
    name: str
    id: uuid.UUID
    shops: list[ShopDetail]
    created: datetime


class ManagedShopDetail(BaseModel):
    id: uuid.UUID
    location: str
    business: str
    permissions: dict[str, list]
    assigned: datetime


class Profile(Account):
    is_active: bool
    is_verified: bool
    business: None | list[BusinessDetail] = Field(default=None)
    managed_shops: None | list[ManagedShopDetail] = Field(default=None)


class Token(BaseModel):
    access_token: str
    token_type: str


class Login(BaseModel):
    email: EmailStr
    password: str


class Shop(BaseModel):
    id: uuid.UUID
    manager: str | None
    location: str


class BusinessProfile(BaseModel):
    id: uuid.UUID
    name: str
    owner: str
    shops: list[Shop]


class SettingOut(BaseModel):
    name: str
    value: str | int
    tag: str | None
    description: str


class SettingIn(BaseModel):
    name: str
    value: str | int


class EntitySetting(BaseModel):
    id: uuid.UUID
    settings: list[SettingOut]


class ShopSetting(EntitySetting):
    pass


class BusinessSetting(EntitySetting):
    pass


class ManagerPermissions(BaseModel):
    sales: list[str]
    inventory: list[str]
    orders: list[str]
    tracker: list[str]
    analytics: list[str]


class CreateInviteToken(BaseModel):
    email: str
    permissions: Union[str, ManagerPermissions]


class Invite(BaseModel):
    for_: str = Field(alias="for")
    created: datetime
    used: bool = Field(serialization_alias="acknowledge")
    expired: bool
    token: str
    sent: bool


class ShopInvite(BaseModel):
    id: uuid.UUID
    location: str
    invite: Invite


class BusinessInvite(BaseModel):
    id: uuid.UUID
    shops: list[ShopInvite]


class InviteAccept(BaseModel):
    token_str: str
    email: str
    firstname: str
    lastname: str
    password: str


class AuditDetails(BaseModel):
    id: int
    name: str
    description: str
    time: datetime
    payload: dict


class TimeLine(BaseModel):
    audit_id: int
    name: str
    description: str
    time: datetime


class BusinessTimeLine(BaseModel):
    id: uuid.UUID
    timeline: list[TimeLine]


class ShopAdd(BaseModel):
    location: str


class ShopRemove(BaseModel):
    shop_id: uuid.UUID
