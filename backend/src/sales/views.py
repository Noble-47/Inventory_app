from sqlmodel import select

from sales.db import DB
from sales.domain.models import Sale, SaleAudit


def fetch_sales(shop_id, query=None):
    with DB() as db:
        sales = db.record.fetch_sales(shop_id, query)
        view = {"shop_id" : shop_id, "sales" : []}
        for sale in sales:
            view['sales'].append({
                "ref" : str(sale.ref),
                "firstname" : sale.customer.firstname,
                "lastname" : sale.customer.lastname,
                "phone_number" : sale.customer.phone,
                "date" : sale.date,
                "units" : [product.model_dump() for product in sale.products],
                "selling_price" : sale.selling_price,
                "amount_paid" : sale.amount_paid,
                "payment_completed" : (sale.selling_price <= sale.amount_paid)
            })
        return view


def get_sale_detail(shop_id, ref):
    with DB() as db:
        sale = db.record.get_sale_detail(shop_id, ref)
        if sale:
            return {
                "shop_id" : shop_id,
                "ref" : str(sale.ref),
                "firstname" : sale.customer.firstname,
                "lastname" : sale.customer.lastname,
                "phone_number" : sale.customer.phone,
                "units" : [product.model_dump() for product in sale.products],
                "date" : sale.date,
                "selling_price" : sale.selling_price,
                "amount_paid" : sale.amount_paid,
                "payment_completed" : (sale.selling_price <= sale.amount_paid)
            }


def get_sale_history(shop_id):
    with DB() as db:
        history = db.record.get_sale_history(shop_id)
        if history is None:
            return
        view = {"shop_id" : shop_id, 'logs' : []}
        for log in history:
            view['logs'].append({
                "audit_id" : log.id,
                "ref" : str(sale.ref),
                "description" : log.description,
                "time" : log.time,
                "payload" : log.payload
            })
        return view
