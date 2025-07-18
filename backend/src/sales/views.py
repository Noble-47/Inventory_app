from sqlmodel import select

from sales.db import db_session
from sales.domain.models import Sale, SaleAudit


def fetch_sales(shop_id):
    session = next(db_session())
    sales = session.exec(
        select(Sale).where(Sale.shop_id == shop_id)
    ).all()
    view = {"shop_id" : shop_id, "sales" : []}
    for sale in sales:
        view['sales'].append({
            "ref" : sale.ref,
            "customer_name" : sale.customer.fullname,
            "customer_phone" : sale.customer.phone,
            "date" : sale.date,
            "units" : sale.products,
            "selling_price" : sale.selling_price,
            "amount_paid" : sale.amount_paid,
            "payment_complete" : (sale.selling_price > sale.amount_paid)
        })
    session.close()
    return view


def get_sale_detail(shop_id, ref):
    session = next(db_session())
    sale = session.exec(
        select(Sale)
        .where(Sale.ref == ref, Sale.shop_id == shop_id)
    ).first()
    session.close()
    if sale:
        return {
            "ref" : sale.ref,
            "customer_name" : sale.customer.fullname,
            "customer_phone" : sale.customer.phone,
            "units" : sale.products,
            "date" : sale.date,
            "selling_price" : sale.selling_price,
            "amount_paid" : sale.amount_paid,
            "payment_completed" : (sale.selling_price > sale.amount_paid)
        }


def get_sale_history(shop_id):
    session = next(db_session())
    history = session.exec(
        select(SaleAudit).where(SaleAudit.shop_id == shop_id)
    ).all()
    session.close()
    if history is None:
        return
    view = {"shop_id" : shop_id, 'logs' : []}
    for log in history:
        view['logs'].append({
            "ref" : log.ref,
            "description" : log.description,
            "time" : log.time,
            "payload" : log.payload
        })
    return view
