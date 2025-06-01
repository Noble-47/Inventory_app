import uuid

from sqlmodel import SQLModel, Field, Session
from sqlmodel import select

from shopify.domain import models
from shopify.db import BaseRepo


class Shop(BaseRepo):

    # def _create(location: str):
    #    shop = Shop(location=location)
    #    return shop

    def _get(id: uuid.UUID):
        shop = self.session.get(models.Shop, id)
        return shop

    def get_by_location(location: str):
        shop = self.session.exec(
            select(models.Shop).where(models.Shop.location == location)
        ).first()
        return shop
