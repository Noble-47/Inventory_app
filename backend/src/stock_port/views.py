from uuid import UUID
from sqlmodel import select

from stock_port.domain.models import Record
from stock_port import db


def get_orders(shop_id):
    session = next(db.db_session())
    record_db = db.RecordDB(session)
    orders = record_db.list_orders(shop_id)
    return {"shop_id": shop_id, "orders": [order.model_dump() for order in orders]}


def get_order_details(shop_id, order_id: UUID):
    session = next(db.db_session())
    record_db = db.RecordDB(session)
    order = record_db.get_order(shop_id=shop_id, order_id=order_id)
    if order:
        view = {}
        view["orderline"] = [b.model_dump() for b in order.batchline]
        view["supplier_firstname"] = order.supplier.firstname
        view["supplier_lastname"] = order.supplier.lastname
        view["supplier_phone"] = order.supplier.phone
        view["expected_delivery_date"] = order.expected_delivery_date
        view["delivery_date"] = order.delivery_date
        view["cost"] = order.cost
        view["status"] = order.status

    return view


def get_suppliers(shop_id):
    session = next(db.db_session())
    record_db = db.RecordDB(session)
    suppliers = record_db.list_suppliers(shop_id)
    return {
        "shop_id": shop_id,
        "suppliers": [supplier.model_dump() for supplier in suppliers],
    }


def get_supplier_details(shop_id, supplier_id):
    session = next(db.db_session())
    record_db = db.RecordDB(session)
    supplier = record_db.get_supplier(shop_id=shop_id, supplier_id=supplier_id)
    if supplier:
        return supplier.model_dump()


def get_shop_history(shop_id):
    session = next(db.db_session())
    audit_db = db.AuditDB(session)
    history = audit_db.fetch(shop_id)
    return {"shop_id": shop_id, "logs": [log.model_dump() for log in history]}
