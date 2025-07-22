from sqlmodel import select

from sales.domain.models import Sale, SaleProductLink, Record
from sales.domain import events
from sales import exceptions


class SalesDB:

    def __init__(self, session, events):
        self.session = session
        self.events = events

    def is_deleted(self, shop_id):
        return self.session.exec(
            select(Record.deleted).where(Record.shop_id == shop_id)
        ).first() or False # if None

    def add(self, shop_id, products, customer, selling_price, amount_paid):
        if self.is_deleted(shop_id):
            raise exceptions.ShopRecordNotFound()

        products = [SaleProductLink(**product) for product in products]
        sale = Sale(shop_id=shop_id, customer=customer, selling_price=selling_price, products=products, amount_paid=amount_paid)
        print()
        print(sale)
        print()
        event = events.NewSaleAdded(
            shop_id=shop_id,
            sale_ref=sale.ref,
            date=sale.date,
            amount_paid=amount_paid,
            firstname=customer.firstname,
            lastname=customer.lastname,
            customer_phone=customer.phone,
            selling_price=sale.selling_price,
            products = [unit.model_dump() for unit in products]
        )
        self.session.add(sale)
        self.events.append(event)

    def delete(self, shop_id, ref):
        sale = get(shop_id, ref)
        self.session.delete(sale)
        self.events.append(
            events.SaleRecordDelete(shop_id=shop_id, sale_reg=ref)
        )


    def get(self, shop_id, ref):
        if not self.is_deleted(shop_id):
            raise exceptions.ShopRecordNotFound()
        stmt = select(Sale).where(Sale.shop_id == shop_id, Sale.ref == ref)
        sale = self.session.exec(stmt).first()
        if sale is None:
            raise exceptions.SaleRecordNotFound()
        return sale

    def update(self, shop_id, ref, updates):
        sale = self.get(shop_id, ref)
        for kw, value in updates.items():
            if hasattr(sale, kw):
                settatr(sale, kw, value)
        self.session.add(sale)
        self.events.append(
            events.SaleRecordUpdated(shop_id=shop_id, sale_ref=ref, updates=updates)
        )
