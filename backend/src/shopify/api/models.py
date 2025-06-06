from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Account(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr


class AccountCreate(Account):
    password: str


class AccountBusinessProfile(BaseModel):
    id: uuid.UUID
    shops: dict[str, uuid.UUID]
    created: datetime


class AccountShopProfile(BaseModel):
    id: uuid.UUID
    permissions: dict[str, list]
    assigned: datetime


class Profile(Account):
    is_active: bool
    is_verified: bool
    business: dict[str, AccountBusinessProfile]
    managed_shops: dict[str, AccountShopProfile]


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
    shops: list[ShopSetting]


class Invite(BaseModel):
    for_: str = Field(alias="for")
    created: datetime
    used: bool
    expired: bool
    token: str


class ShopInvite(BaseModel):
    id: uuid.UUID
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


class CreateInviteToken(BaseModel):
    email: str
    permissions: str | dict[str, list[str]]
