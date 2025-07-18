from sqlalchemy import select

from inventory.domain.models import Inventory


class InventoryDB:

    def __init__(self, session, events=None):
        self.session = session

    def exists(self, shop_id):
        stmt = select(Inventory.shop_id).where(Inventory.shop_id == shop_id)
        return bool(self.session.scalars(stmt).first())

    def add(self, shop_id):
        inventory = Inventory(shop_id=shop_id)
        self.session.add(inventory)

    def remove(self, shop_id):
        inventory = self.session.scalars(
            select(Inventory).where(Inventory.shop_id == shop_id)
        ).first()
        if inventory:
            self.session.delete(inventory)
