from sqlalchemy import select

from inventory.domain.read_models import StockView
from inventory.adapters.orm import db_session


def verify_exists(shop_id, sku):
    session = next(db_session())
    stock = session.scalars(
        select(StockView.sku).where(StockView.sku == sku, StockView.shop_id == shop_id)
    ).first()
    session.close()
    return bool(stock)


def verify_can_dispatch(shop_id, sku, quantity):
    session = next(db_session())
    stock = session.scalars(
        select(StockView).where(StockView.sku == sku, StockView.shop_id == shop_id)
    ).first()
    session.close()
    if stock:
        return stock.level > quantity
    return False


def get_stock_detail(shop_id, sku):
    session = next(db_session())
    stock = session.scalars(
        select(StockView).where(StockView.sku == sku, StockView.shop_id == shop_id)
    ).first()
    session.close()
    if stock:
        return {
            "name": stock.name,
            "cogs": stock.cogs,
            "value": stock.value,
            "level": stock.level,
            "price": stock.price,
        }
