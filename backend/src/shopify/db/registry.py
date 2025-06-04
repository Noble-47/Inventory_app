import uuid

from sqlmodel import Session, select

from shopify.domain import models
from shopify import db


class Registry(db.BaseRepo):

    def _create(
        self,
        business_id: uuid,
        owner_id: id,
    ):
        registry = models.BusinessRegistry(business_id=business_id, owner_id=owner_id)
        return registry

    def _get(self, business_id: uuid):
        registry = self.session.exec(
            select(models.BusinessRegistry).where(
                models.BusinessRegistry.business_id == business_id
            )
        ).one()
        return registry

    def fetch(self, account_id: int):
        business_record = self.session.exec(
            select(models.BusinessRegistry).where(
                models.BusinessRegistry.owner_id == account_id
            )
        ).all()
        managerial_record = self.session.exec(
            select(models.ShopRegistry).where(
                models.ShopRegistry.manager_id == account_id
            )
        ).all()
        records = {
            "business": [record.model_dump() for record in business_record],
            "managed_shops": [record.model_dump() for record in managerial_record],
        }
        for business in records['business']:
            business_id = business['business_id']
            business['shops'] = self.session.exec(select(models.ShopRegistry.shop_id).where(models.ShopRegistry.business_id == business_id)).all()
        return records
