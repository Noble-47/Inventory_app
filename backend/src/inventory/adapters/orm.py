from sqlalchemy import Boolean, ForeignKey, Integer, Float, String, DateTime, Enum
from sqlalchemy.orm import registry, relationship
from sqlalchemy import Table, Column, event

from inventory.domain.models import Stock, Batch, MeasurementMetric
from inventory.settings import get_control_strategy

mapper_registry = registry()
metadata = mapper_registry.metadata

batch_table = Table(
    "batch",
    metadata,
    Column("ref", String(30), primary_key=True),
    Column("sku", ForeignKey("stock.sku")),
    Column("stock_in_units", Integer),
    Column("quantity", Integer),
    Column("price", Float),
    Column("stock_time", DateTime),
)

stock_table = Table(
    "stock",
    metadata,
    Column("sku", String(30), primary_key=True),
    Column("name", String, nullable=False),
    Column("version_number", Integer, default=0, nullable=False),
    Column("metric", Enum(MeasurementMetric)),
    Column("offset", Integer, default=0),
    Column("last_sale", DateTime, nullable=True),
)

inventory_view_table = Table(
    "inventory_view",
    metadata,
    Column("sku", String(30), primary_key=True),
    Column("name", String, nullable=False),
    Column("level", Integer, nullable=False),
    Column("last_sale", DateTime, nullable=True),
    Column("inventory_value", Float, nullable=False, default=0.0)
)


def start_mappers():
    mapper_registry.map_imperatively(Batch, batch_table)
    mapper_registry.map_imperatively(
        Stock,
        stock_table,
        properties={
            "batches": relationship(
                Batch,
                #lazy="select" # load batches only when needed
            ),
        },
        version_id_col=stock_table.c.version_number,
        version_id_generator=False,
    )


@event.listens_for(Stock, "load")
def stock_config(stock, context):
    # get control strategy for stock
    control_strategy = get_control_strategy(stock.sku)
    stock.set_control_strategy(control_strategy)
    stock.events = []
