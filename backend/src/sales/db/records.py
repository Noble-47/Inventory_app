from collections import defaultdict

from sqlmodel import select

from sales.domain.models import (
    Record,
    Sale,
    SaleAudit,
    Customer,
    SaleProductLink,
    Product,
)


class RecordsDB:

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
            select(Record).where(Record.shop_id == shop_id, Record.deleted == False)
        ).first()

    def is_deleted(self, shop_id):
        return not bool(self.get(shop_id))

    def fetch_sales(self, shop_id):
        stmt = select(Sale).where(Sale.shop_id == shop_id)
        results = self.session.exec(stmt).all()
        return results

    def get_sale_detail(self, shop_id, ref):
        if self.is_deleted(shop_id):
            return

        return self.session.exec(
            select(Sale).where(Sale.ref == ref, Sale.shop_id == shop_id)
        ).first()

    def get_sale_history(self, shop_id):
        if self.is_deleted(shop_id):
            return

        return self.session.exec(
            select(SaleAudit).where(SaleAudit.shop_id == shop_id)
        ).all()

    def get_customers(self, shop_id):
        if self.is_deleted(shop_id):
            return

        customer_record = self.session.exec(
            select(Customer, Sale).join(Sale).where(Sale.shop_id == shop_id)
        ).all()

        grouped = defaultdict(list)
        for customer, purchase in customer_record:
            grouped[customer].append(purchase)
        return list(grouped.items())
