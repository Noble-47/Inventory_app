from sqlmodel import select

from stock_port.domain.models import Supplier, ShopSupplier


class SupplierDB:

    def __init__(self, session):
        self.session = session

    def _get(self, supplier_phone):
        supplier = self.session.exec(
            select(Supplier).where(Supplier.phone == supplier_phone)
        ).first()
        return supplier

    def get(self, shop_id, firstname, lastname, phone):
        supplier = self._get(phone)
        if supplier is None:
            supplier = Supplier(firstname=firstname, lastname=lastname, phone=phone)
        shop_record = self.session.exec(
            select(ShopSupplier).where(
                ShopSupplier.supplier_phone == supplier.phone,
                ShopSupplier.shop_id == shop_id,
            )
        ).first()
        if shop_record is None:
            shop_record = ShopSupplier(shop_id=shop_id, supplier_phone=supplier.phone)
            self.session.add(shop_record)
            self.session.flush()
        self.session.add(supplier)
        return shop_record
