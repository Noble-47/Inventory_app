from __future__ import annotations
from functools import partial
from datetime import datetime
import pytz
import uuid

from sqlmodel import SQLModel, Field, Relationship

from shopify import config

class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str
    lastname: str
    email: str = Field(index=True, unique=True)
    password_hash: str
    is_active: bool = True
    is_verified: bool = False

    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True

    def __repr__(self):
        return f"{self.firstname.title()} {self.lastname.title()}"


class Shop(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    location: str = Field(index=True)
    business_id: uuid.UUID = Field(foreign_key="business.id")
    is_active : bool = True
    manager_id: int | None = Field(default=None, foreign_key="account.id")
    manager: Account | None = Relationship()

    def assign_manager(manager: Account):
        self.manager = manager
        self.manager_id = manager.id

    def dismiss_manager():
        if self.manager:
            manager = self.manager
            manager.active = False
            self.manager = None
            self.manager_id = None


class Registry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    entity_id: uuid.UUID = Field(unique=True)
    account_id: int | None = Field(foreign_key="account.id")
    entity_type: str
    entity_name: str
    permissions: str
    registration_date: datetime = Field(
        default_factory=partial(datetime.now, tz=config.TIMEZONE)
    )


class Business(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    owner_id: int = Field(foreign_key="account.id")
    owner: Account = Relationship()
    shops: list[Shop] = Relationship()

    def add_shop(self, location: str):
        shop = Shop(location=location, business_id=self.id)
        self.shops.append(shop)
        self.events.append(events.AddedNewShop(self.id, shop.id, shop.location))
        return shop

    def get_shop(self, shop_id):
        try:
            shop = next(shop for shop in self.shops if shop.id == shop_id)
        except StopIteration:
            raise ValueError(f"Shop Not Found, {shop_id} in Business {self.id}")
        return shop

    def remove_shop(self, shop_id: uuid):
        shop = get_shop(self, shop_id)
        shops.remove(shop)
        shop.is_active = False
        self.events.append(events.RemovedShop(self.id, shop.location))

    def assign_shop_manager(
        self, shop_id: uuid, account: Account
    ):
        shop = self.get_shop(shop_id)
        if shop.manager is not None:
            self.dismiss_shop_manager(shop=shop)
        shop.assign_manager(account)
        self.events.append(events.AssignedNewManager(self.id, account.id))

    def dismiss_shop_manager(
        self, shop_id: uuid | None = None, shop: Shop | None = None
    ):
        if shop_id and (shop is None):
            shop = self.get_shop(shop_id)
        elif not (shop_id or shop):
            raise ValueError(
                f"Missing shop_id and shop. Specify either of the shop or the shop_id"
            )
        shop.dimiss_manager()
        self.events.append(events.DismissedManager(self.id, shop.id))
