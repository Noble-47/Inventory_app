from sqlmodel import select

from sales.domain.models import Sale, SaleProductLink
from sales.domain import events
from sales import exceptions


class SalesDB:

    def __init__(self, session, events=None):
        self.session = session
        self.events = events or []

    def add(self, shop_id, products, customer, selling_price, amount_paid):
        products = SaleProductLink(**products)
        sale = Sale(shop_id=shop_id, customer=customer, selling_price=selling_price, date=date, products=products)
        event = events.NewSaleAdded(
            shop_id=shop_id,
            sale_ref=sale.ref,
            date=sale.date,
            amount_paid=amount_paid,
            customer=customer.fullname,
            cutomer_phone=customer.phone
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
