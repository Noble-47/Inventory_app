from sqlalchemy.orm import selectinload
from sqlmodel import select

from stock_port.domain.models import Record, Supplier, ShopSupplier, Order, BatchLine


class RecordDB:

    def __init__(self, session):
        self.session = session

    def create(self, shop_id):
        if self.get(shop_id):
            return
        record = Record(shop_id=shop_id)
        self.session.add(record)

    def delete(self, shop_id):
        record = self.get(shop_id)
        if record is None:
            return
        record.deleted = True

    def get(self, shop_id):
        return self.session.exec(
            select(Record)
            .where(Record.shop_id == shop_id, Record.deleted == False)
            .options(selectinload(Record.orders).selectinload(Order.supplier))
        ).first()

    def is_deleted(self, shop_id):
        return not bool(self.get(shop_id))

    def list_orders(self, shop_id):
        record = self.get(shop_id)
        if record:
            return record.orders
        return []

    def get_order(self, shop_id, order_id):
        if not self.is_deleted(shop_id):
            return self.session.exec(
                select(Order).where(Order.id == order_id, Order.shop_id == shop_id)
            ).first()

    def list_suppliers(self, shop_id):
        shop_record = self.get(shop_id)
        if shop_record:
            return shop_record.suppliers
        return []

    def get_supplier(self, shop_id, supplier_id):
        if not self.is_deleted(shop_id):
            stmt = (
                select(Supplier)
                .join(ShopSupplier)
                .where(Supplier.id == supplier_id)
                .where(ShopSupplier.shop_id == shop_id)
            )
        return self.session.exec(stmt).first()
