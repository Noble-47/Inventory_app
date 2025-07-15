from dataclasses import asdict

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from inventory import config
from inventory.domain.read_models import StockView, InventoryView


engine = create_async_engine(
    config.get_async_url(),
    # pool_class=AsyncAdaptableQueuePool,
    pool_size=20,
    max_overflow=10,
)

async_session = async_sessionmaker(engine)


async def get_inventory_view(shop_id):
    async with async_session() as session:
        result = await session.scalars(
            select(InventoryView).where(InventoryView.shop_id == str(shop_id))
        )
        inventory = result.first()
        if inventory:
            return inventory.model_dump()


async def get_stock_view(shop_id, sku):
    async with async_session() as session:
        result = await session.scalars(
            select(StockView).where(
                StockView.sku == sku, StockView.shop_id == str(shop_id)
            )
        )
        stock = result.first()
        if stock:
            return stock.model_dump()
