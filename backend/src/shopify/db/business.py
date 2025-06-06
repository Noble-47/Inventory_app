import uuid

from sqlmodel import Session
from sqlmodel import select

from shopify.domain import models
from shopify.domain import events
from shopify import db


class Business(db.BaseRepo):

    seen = set()

    def _create(self, name: str, owner: models.Account):
        business = models.Business(name=name, owner=owner)
        self.events.append(
            events.NewBusinessCreated(
                business_id=business.id,
                name=name,
                owner_email=owner.email,
                owner_name=owner.fullname,
            )
        )
        self.seen.add(business)
        return business

    def _get(self, id: uuid.UUID):
        business = self.session.exec(
            select(models.Business).where(models.Business.id == id)
        ).one()
        self.seen.add(business)
        return business

    def check_name_exists(self, owner_id: uuid.UUID, name: str):
        return (
            self.session.exec(
                select(models.Business.id).where(
                    models.Business.owner_id == owner_id, models.Business.name == name
                )
            ).first()
            is not None
        )
