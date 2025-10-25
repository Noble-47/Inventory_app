import uuid

from sqlmodel import Session, select

from shopify.db import db_session
from shopify.domain.read_models import BusinessView, ShopView


class View:

    def __init__(self, session: Session):
        self.session = session

    def add_shop(
        self,
        business_id: uuid.UUID,
        shop_id: uuid.UUID,
        shop_location: str,
    ):
        view = ShopView(
            business_id=business_id,
            shop_id=shop_id,
            location=shop_location,
        )
        self.session.add(view)

    def delete_shop(self, business_id: str, location: str):
        view = self.session.exec(
            select(ShopView).where(
                ShopView.business_id == business_id, ShopView.location == location
            )
        ).first()
        if view:
            self.session.delete(view)

    def add_business(
        self, business_id: uuid.UUID, business_name: str, owner_id: int, owner_name: str
    ):
        view = BusinessView(
            business_id=business_id,
            name=business_name,
            owner_name=owner_name,
            owner_id=owner_id,
        )
        self.session.add(view)

    def add_manager_to_shop(self, shop_id: uuid.UUID, manager: str, manager_email: str):
        view = self.session.exec(
            select(ShopView).where(ShopView.shop_id == shop_id)
        ).first()
        if view:
            view.manager = manager
            view.manager_email = manager_email

    def remove_manager_from_shop(self, shop_id: uuid.UUID):
        view = self.session.exec(
            select(ShopView).where(ShopView.shop_id == shop_id)
        ).first()
        if view:
            view.manager = None
            view.manager_email = None
