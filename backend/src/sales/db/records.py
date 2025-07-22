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
        return bool(self.get(shop_id))

    def fetch_sales(self, shop_id, query):
        stmt = (
            select(Sale)
            .join(Customer, isouter=True)
            .join(SaleProductLink, isouter=True)
            .join(Product, isouter=True)
        )

        if query.firstname:
            stmt = stmt.where(Customer.firstname.ilike(query.firstname))

        if query.lastname:
            stmt = stmt.where(Customer.lastname.ilike(query.lastname))

        if query.phone_number:
            stmt = stmt.where(Customer.phone == query.phone_number)

        if query.product:
            stmt = stmt.where(Product.name.ilike(query.product))

        if query.sku:
            stmt = stmt.where(Product.name.ilike(query.sku))

        if query.start_date:
            stmt = stmt.where(Sale.date >= query.start_date)

        if query.end_date:
            stmt = stmt.where(Sale.date <= query.end_date)

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
