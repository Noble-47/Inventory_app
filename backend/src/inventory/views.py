from dataclasses import asdict
from sqlalchemy import select

from inventory.domain.read_models import StockView, InventoryView
from inventory.adapters.orm import db_session
from inventory.adapters import audit


def get_inventory_view(shop_id):
    session = next(db_session())
    result = session.scalars(
        select(InventoryView).where(InventoryView.shop_id == str(shop_id))
    ).first()
    if inventory:
        return inventory.model_dump()


def get_stock_view(shop_id, sku):
    session = next(db_session())
    stock = session.scalars(
        select(StockView).where(StockView.sku == sku, StockView.shop_id == str(shop_id))
    ).first()
    if stock:
        return stock.model_dump()


# def get_inventory_history(shop_id):
#    session = get_session()
#    shop_audit = audit.ShopAudit(session)
#    shop_history = shop_audit.fetch(shop_id)
#    view = {'shop_id' : shop_id}
#    view['stock_logs'] = [entry for entry in history]
#    return view


def get_stock_history(shop_id, sku):
    session = next(db_session())
    stock_audit = audit.StockAudit(session)
    stock_history = stock_audit.fetch(shop_id, sku)
    view = {"shop_id": shop_id, "sku": sku}
    view["logs"] = [history.model_dump() for history in stock_history]
    return view


def get_batch_history(shop_id, sku, batch_ref):
    session = next(db_session())
    batch_audit = audit.BatchAudit(session)
    batch_history = batch_audit.fetch(shop_id, sku, batch_ref)
    view = {"shop_id": shop_id, "sku": sku, "batch_ref": batch_ref}
    view["logs"] = [history.model_dump() for history in batch_history]
    return view
