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
        records = {"business": [record.model_dump() for record in business_record]}
        records["managed_shops"] = []
        for business in records["business"]:
            business_id = business["business_id"]
            shops = self.session.exec(
                select(models.ShopRegistry.shop_id, models.ShopRegistry.location).where(
                    models.ShopRegistry.business_id == business_id
                )
            ).all()
            business["shops"] = dict((shop[1], shop[0]) for shop in shops)

        managerial_records = self.session.exec(
            select(
                models.ShopRegistry.shop_id,
                models.ShopRegistry.location,
                models.ManagerRegistry,
            )
            .select_from(models.ShopRegistry)
            .join(
                models.ManagerRegistry, models.ManagerRegistry.manager_id == account_id
            )
            .where(
                models.ShopRegistry.manager_id == account_id,
            )
        ).all()

        for record in managerial_records:
            shop_id, location, manager_record = record
            manager_record = manager_record.model_dump()
            manager_record.update({"location": location, "id": shop_id})
            records["managed_shops"].append(manager_record)

        return records

    def get_shop_parent(self, shop_id: uuid.UUID):
        business_id = self.session.exec(
            select(models.ShopRegistry.business_id).where(
                models.ShopRegistry.shop_id == shop_id
            )
        ).first()
        return business_id
