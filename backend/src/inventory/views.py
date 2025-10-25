from dataclasses import asdict
import json

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from inventory import config
from inventory.domain.models import Batch
from inventory.adapters.audit import StockLog, BatchLog
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


async def get_stock_history(shop_id, sku):
    """List of batch events related to product."""
    async with async_session() as session:
        result = await session.scalars(
            select(StockLog).where(
                StockLog.sku == sku, StockLog.shop_id == str(shop_id)
            )
        )
        audit = result.all()
        view = {"shop_id": shop_id, "sku": sku, "logs": []}
        for stock in audit:
            view["logs"].append(
                {
                    "time": stock.event_time,
                    "audit_id": stock.id,
                    "payload": json.loads(stock.payload),
                    "description": stock.description,
                }
            )
        return view


async def get_batch(shop_id, sku, ref):
    "List of batch and batch events"
    shop_id = str(shop_id)
    async with async_session() as session:
        result = await session.scalars(
            select(Batch).where(
                Batch.ref == ref, Batch.sku == sku, Batch.shop_id == shop_id
            )
        )
        batch = result.first()
        if batch is None:
            return
        history = await session.scalars(
            select(BatchLog).where(
                BatchLog.batch_ref == ref,
                BatchLog.sku == sku,
                BatchLog.shop_id == shop_id,
            )
        )
        history = history.all()

        view = asdict(batch)
        view["shop_id"] = shop_id
        view["logs"] = []
        for log in history:
            view["logs"].append(
                {
                    "time": log.event_time,
                    "audit_id": log.id,
                    "payload": json.loads(log.payload),
                    "description": log.description,
                }
            )
        return view
