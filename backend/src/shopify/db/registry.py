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
        records["manager_record"] = []
        for business in records["business"]:
            business_id = business["business_id"]
            shops = self.session.exec(
                select(models.ShopRegistry.shop_id, models.ShopRegistry.location).where(
                    models.ShopRegistry.business_id == business_id,
                    models.ShopRegistry.deleted == False,
                )
            ).all()
            business["shops"] = dict((shop[1], shop[0]) for shop in shops)

        managerial_records = self.session.exec(
            select(
                models.ShopRegistry.business_id,
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
                models.ShopRegistry.deleted == False,
                models.ManagerRegistry.is_active == True,
            )
        ).all()

        for record in managerial_records:
            business_id, shop_id, location, manager_record = record
            manager_record = manager_record.model_dump()
            manager_record.update(
                {"location": location, "id": shop_id, "business_id": business_id}
            )
            records["manager_record"].append(manager_record)

        return records

    def get_shop_parent(self, shop_id: uuid.UUID):
        business_id = self.session.exec(
            select(models.ShopRegistry.business_id).where(
                models.ShopRegistry.shop_id == shop_id
            )
        ).first()
        return business_id

    def get_shop_manager(self, shop_id: uuid.UUID):
        shop_registry = self.session.exec(
            select(models.ShopRegistry).where(
                models.ShopRegistry.shop_id == shop_id,
                models.ManagerRegistry.is_active == True,
            )
        ).first()
        if shop_registry and shop_registry.manager is not None:
            return shop_registry.manager.fullname
        return None

    def get_managers(self, business_id: uuid.UUID):
        shop_with_managers = self.session.exec(
            select(models.ShopRegistry, models.ManagerRegistry.assigned)
            .join(models.ManagerRegistry)
            .where(
                models.ShopRegistry.manager_id != None,
                models.ManagerRegistry.is_active == True,
            )
        ).all()
        return shop_with_managers

    def get_shop_registry(self, business_id, shop_id):
        return self.session.exec(
            select(models.ShopRegistry).where(
                models.ShopRegistry.business_id == business_id,
                models.ShopRegistry.shop_id == shop_id,
            )
        ).first()

    def get_manager_registry(self, business_id, shop_id):
        return self.session.exec(
            select(models.ManagerRegistry).where(
                models.ManagerRegistry.business_id == business_id,
                models.ManagerRegistry.shop_id == shop_id,
            )
        ).first()
