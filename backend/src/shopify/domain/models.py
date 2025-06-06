from functools import partial
from datetime import datetime
from typing import ClassVar
import pytz
import uuid

from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from pydantic import model_serializer, ConfigDict

from shopify import config
from shopify import exceptions
from shopify import permissions as permissions_mod
from shopify.domain import events

datetime_now_utc = partial(datetime.now, config.TIMEZONE)


class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str
    lastname: str
    email: str = Field(index=True, unique=True)
    password_hash: str
    type: str = Field(default="manager", alias="type")
    is_active: bool = True
    is_verified: bool = False

    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}".title().strip()

    @model_serializer
    def serialize_model(self):
        return {
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
        }

    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True

    def __repr__(self):
        return f"{self.firstname.title()} {self.lastname.title()}"


class ShopRegistry(SQLModel, table=True):
    __tablename__ = "shop_registry"
    __table_args__ = (UniqueConstraint("business_id", "location"),)

    id: int | None = Field(default=None, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="business.id")
    shop_id: uuid.UUID = Field(unique=True, default_factory=uuid.uuid4)
    location: str = Field(index=True)
    manager_id: int | None = Field(foreign_key="account.id", default=None)
    permissions: str | None = Field(default=None)
    assigned: datetime | None
    deleted: bool = False

    manager: Account = Relationship()

    @model_serializer
    def serialize_model(self):
        return {
            "shop_id": self.shop_id,
            "permissions": permissions_mod.parse_permission_str(self.permissions),
            "location": self.location,
            "manager": self.manager.fullname,
            "assigned": self.assigned,
        }


class Business(SQLModel, table=True, frozen=True):
    __table_args__ = (UniqueConstraint("owner_id", "name"),)
    __hash__ = object.__hash__
    model_config = ConfigDict(extra="allow")

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    owner_id: int = Field(foreign_key="account.id")
    owner: Account = Relationship()
    registry: list[ShopRegistry] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(ShopRegistry.business_id == Business.id, ShopRegistry.deleted == False)"
        }
    )
    events: ClassVar[list] = []

    def search_registry(self, shop_id):
        record = next(record for record in self.registry if record.shop_id == shop_id)
        return record

    def add_shop(self, location: str):
        shop = ShopRegistry(location=location, business_id=self.id)
        if any(location == record.location for record in self.registry):
            raise exceptions.DuplicateShopRecord("Duplicate Shop Location")
        self.registry.append(
            ShopRegistry(business_id=self.id, shop_id=shop.shop_id, location=location)
        )
        self.events.append(
            events.AddedNewShop(
                business_id=self.id, shop_id=shop.shop_id, shop_location=shop.location
            )
        )
        return shop

    def remove_shop(self, shop_id: uuid):
        record = self.search_registry(shop_id)
        record.deleted = True
        self.events.append(
            events.RemovedShop(business_id=self.id, location=record.location)
        )

    def assign_shop_manager(self, shop_id: uuid, account: Account, permissions: str):
        record = self.search_registry(shop_id)
        if record.manager_id is not None:
            raise exceptions.ShopAlreadyHasAManager("Shop Already Has A Manager")
        record.manager_id = account.id
        record.permissions = permissions_mod.create_permission_str(permissions)
        record.assigned = datetime.now(config.TIMEZONE)
        self.events.append(
            events.AssignedNewManager(
                business_id=self.id,
                manager_email=account.email,
                manager_name=account.fullname,
                shop_location=record.location,
                shop_id=record.shop_id,
            )
        )

    def dismiss_shop_manager(self, shop_id: uuid.UUID):
        record = self.search_registry(shop_id)
        record.manager_id = None
        record.permissions = None
        record.assigned = None
        self.events.append(
            events.DismissedManager(
                business_id=self.id, shop_id=shop.id, shop_location=record.location
            )
        )


class BusinessRegistry(SQLModel, table=True):
    __tablename__ = "business_registry"
    id: int | None = Field(default=None, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="business.id", unique=True)
    owner_id: int = Field(foreign_key="account.id")
    created: datetime = Field(default_factory=datetime_now_utc)

    business: Business = Relationship()

    @model_serializer
    def serialize_model(self):
        return {
            "business_id": self.business_id,
            "business_name": self.business.name,
            "created": self.created,
        }
