from sqlalchemy import (
    Boolean,
    Integer,
    Float,
    String,
    DateTime,
    Enum,
    ForeignKeyConstraint,
    UniqueConstraint,
)

from sqlalchemy.orm import registry, relationship, column_property
from sqlalchemy import Table, Column, event, select
from sqlalchemy import create_engine

from inventory.settings import get_control_strategy
from inventory.config import get_database_url

from inventory.domain.models import Stock, Batch
from inventory.adapters.audit import StockLog, BatchLog
from inventory.domain.read_models import StockView, InventoryView


mapper_registry = registry()
metadata = mapper_registry.metadata

batch_table = Table(
    "batch",
    metadata,
    Column("ref", String(30), primary_key=True),
    Column("sku", String(30)),
    Column("shop_id", String(30)),
    Column("stock_in_units", Integer),
    Column("quantity", Integer),  # consider adding an index here
    Column("price", Float),
    Column("stock_time", DateTime),
    ForeignKeyConstraint(
        ["sku", "shop_id"],
        ["stock.sku", "stock.shop_id"],
        ondelete="CASCADE",
    ),
)

stock_table = Table(
    "stock",
    metadata,
    Column("sku", String(30), primary_key=True),
    Column("shop_id", String(30)),
    Column("name", String, nullable=False),
    Column("version_number", Integer, default=0, nullable=False),
    Column("offset", Integer, default=0),
    Column("last_sale", DateTime, nullable=True),
    UniqueConstraint("sku", "shop_id", name="shop_id_stock_sku_uix"),
)

inventory_view_table = Table(
    "inventory_view",
    metadata,
    Column("shop_id", String(30), primary_key=True, unique=True),
    Column("cogs", Float, nullable=False),
    Column("value", Float, nullable=False),
)


stock_view_table = Table(
    "stock_view",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("shop_id", String, nullable=False),
    Column("sku", String, nullable=False, unique=True),
    Column("cogs", Float, nullable=False),
    Column("value", Float, nullable=False),
    Column("level", Integer, nullable=False),
    UniqueConstraint("sku", "shop_id", name="shop_id_stock_sku_uix"),
)

setting_table = Table(
    "inventory_setting",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("shop_id", String, unique=True, nullable=False),
    Column("name", String, unique=True, nullable=False),
    Column("value", String, nullable=False),
)

stock_log_table = Table(
    "stock_log",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("shop_id", String),
    Column("sku", String),
    Column("description", String),
    Column("time", DateTime),
    Column("event_hash", String, unique=True),
    Column("payload", String),
)

batch_log_table = Table(
    "batch_log",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("shop_id", String),
    Column("sku", String),
    Column("batch_ref", String),
    Column("description", String),
    Column("time", DateTime),
    Column("event_hash", String, unique=True),
    Column("payload", String),
)


def create_tables():
    engine = create_engine(get_database_url())
    metadata.create_all(engine)


def start_mappers():
    mapper_registry.map_imperatively(Batch, batch_table)
    mapper_registry.map_imperatively(
        Stock,
        stock_table,
        properties={
            "batches": relationship(
                Batch,
            ),
        },
        version_id_col=stock_table.c.version_number,
        version_id_generator=False,
    )
    mapper_registry.map_imperatively(
        InventoryView,
        inventory_view_table,
        properties={
            "stocks": relationship(
                Stock,
                primaryjoin="and_(Stock.shop_id == Inventory.shop_id)",
            )
        },
    )
    mapper_registry.map_imperatively(
        StockView,
        stock_view_table,
        properties={
            "batches": relationship(
                Batch,
                primaryjoin="and_(Batch.sku == StockView.sku, Batch.shop_id == StockView.shop_id)",
            ),
            "last_sale": column_property(
                select(stock_table.c.last_sale)
                .where(stock_table.c.sku == stock_view_table.c.sku)
                .where(stock_table.c.shop_id == stock_view_table.c.shop_id)
                .correlate_except(stock_table)
                .scalar_subquery()
            ),
        },
    )
    mapper_registry.map_imperatively(BatchLog, batch_log_table)
    mapper_registry.map_imperatively(StockLog, stock_log_table)


@event.listens_for(Stock, "load")
def stock_config(stock, context):
    # get control strategy for stock
    control_strategy = get_control_strategy(stock.shop_id)
    stock.set_control_strategy(control_strategy)
    stock.events = []
