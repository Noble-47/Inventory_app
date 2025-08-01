from sqlalchemy import select

from inventory.domain.read_models import StockView
from inventory.adapters.orm import db_session
from inventory.domain.models import Stock


def verify_exists(shop_id, sku):
    shop_id = str(shop_id)
    session = next(db_session())
    stock = session.scalars(
        select(StockView.sku).where(StockView.sku == sku, StockView.shop_id == shop_id)
    ).first()
    session.close()
    return bool(stock)


def ensure_exists(shop_id, sku):
    shop_id = str(shop_id)
    session = next(db_session())
    stock = session.scalars(
        select(StockView.sku).where(StockView.sku == sku, StockView.shop_id == shop_id)
    ).first()
    if stock:
        session.close()
        return True
    # check global stock record for sku
    stock = session.scalars(select(Stock).where(Stock.sku == sku)).first()
    if stock is None:
        session.close()
        return False

    # if global record exists for sku, create local inventory record of stock
    print("Creating zero stock from existing stock found in global record for - {sku}")
    shop_stock = Stock(
        shop_id=shop_id,
        sku=sku,
        name=stock.name,
        brand=stock.brand,
        packet_size=stock.packet_size,
        packet_type=stock.packet_type,
    )
    session.add(shop_stock)
    session.commit()
    session.close()
    return True


def verify_can_dispatch(shop_id, sku, quantity):
    session = next(db_session())
    shop_id = str(shop_id)
    stock = session.scalars(
        select(StockView).where(StockView.sku == sku, StockView.shop_id == shop_id)
    ).first()
    session.close()
    if stock:
        return stock.level > quantity
    return False


def get_stock_detail(shop_id, sku):
    session = next(db_session())
    shop_id = str(shop_id)
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
