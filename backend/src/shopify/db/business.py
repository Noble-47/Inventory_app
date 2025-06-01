from sqlmodel import Session
from sqlmodel import select

from shopify.domain import models
from shopify.domain import events
from shopify import db


class Business(db.BaseRepo):

    def _create(name: str, owner: models.Account):
        business = models.Business(name=name, owner=owner)
        self.events.append(events.NewBusinessCreated(name, owner.id))
        return business

    def _get(name: str):
        business = self.session.exec(
            select(models.Business).where(models.Business.name == name)
        ).one()
        return business
