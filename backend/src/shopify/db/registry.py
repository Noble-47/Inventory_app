import uuid

from sqlmodel import Session, select

from shopify.domain import models
from shopify import db


class Registry(db.BaseRepo):

    def _create(
        self,
        entity_id: uuid,
        entity_name: str,
        entity_type: str,
        account_id: id,
        permissions: str,
    ):
        registry = self.get(entity_id)
        if registry:
            self.update(registry, account_id, permissions)
        else:
            registry = models.Registry(
                entity_id, account_id, entity_type, entity_name, permissions
            )
        return registry

    def _get(self, entity_id: uuid):
        registry = self.session.exec(
            select(models.Registry).where(models.Registry.entity_id == entity_id)
        ).first()
        return registry

    def update(self, registry, account_id, permissions):
        registry.account_id = account_id
        registry.permissions = permissions
        return registry

    def fetch(self, account_id: int):
        records = self.session.exec(
            select(models.Registry).where(models.Registry.account_id == account_id)
        ).all()
        return records
