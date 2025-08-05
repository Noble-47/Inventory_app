from typing import Union, Optional, Literal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Account(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr


class AccountCreate(Account):
    password: str


class ShopDetail(BaseModel):
    id: UUID
    location: str
    manager: str | None = Field(default=None)


class BusinessDetail(BaseModel):
    name: str
    id: UUID
    shops: list[ShopDetail]
    created: datetime


class ManagedShopDetail(BaseModel):
    id: UUID
    location: str
    business: str
    assigned: datetime


class Profile(Account):
    is_active: bool
    is_verified: bool
    business: None | list[BusinessDetail] = Field(default=None)
    managed_shops: None | list[ManagedShopDetail] = Field(default=None)
    account_type: str


class Token(BaseModel):
    access_token: str
    token_type: str


class Login(BaseModel):
    email: EmailStr
    password: str


class Shop(BaseModel):
    id: UUID
    manager: str | None
    location: str


class BusinessProfile(BaseModel):
    id: UUID
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
    id: UUID
    settings: list[SettingOut]


class ShopSetting(EntitySetting):
    pass


class BusinessSetting(EntitySetting):
    pass


class ManagerPermissions(BaseModel):
    sales: list[str]
    inventory: Literal[
        "can_add_new_product",
        "can_delete_product",
        "can_view_inventory_value",
        "can_view_cogs",
    ]
    orders: list[str]
    tracker: list[str]
    analytics: Literal["can_view_profits", "can_view_loss"]


class Manager(BaseModel):
    shop_id: UUID
    shop_location: str
    manager_id: int
    firstname: str
    lastname: str
    assigned: datetime


class CreateInviteToken(BaseModel):
    email: str


class Invite(BaseModel):
    for_: str = Field(alias="for")
    created: datetime
    used: bool = Field(serialization_alias="acknowledge")
    expired: bool
    token: str
    sent: bool


class ShopInvite(BaseModel):
    id: UUID
    location: str
    invite: Invite


class BusinessInvite(BaseModel):
    id: UUID
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
    id: UUID
    timeline: list[TimeLine]


class ShopAdd(BaseModel):
    location: str


class ShopRemove(BaseModel):
    shop_id: UUID
