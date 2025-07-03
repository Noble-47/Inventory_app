import uuid

from sqlmodel import SQLModel, Field, Session
from sqlmodel import select

from shopify.domain.models import ShopRegistry
from shopify.db import BaseRepo


class Shop(BaseRepo):

    def check_shop_exists(location: str, business_id: uuid.UUID):
        return (
            self.session.exec(
                select(ShopRegistry.id).where(
                    ShopRegistry.business_id == business_id,
                    ShopRegistry.location == location,
                )
            ).first()
            is None
        )

    def get_shop_id(self, location:str, business_id: uuid.UUID):
        return (
            self.session.exec(
                select(ShopRegistry.shop_id)
                .where(
                    ShopRegistry.business_id == business_id,
                    ShopRegistry.location == location
                )
            ).first()
        )
