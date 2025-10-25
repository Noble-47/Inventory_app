from sqlalchemy import Integer, String, ForeignKey, DateTime, Float
from sqlalchemy import Table, Column, UniqueConstraint, Relationship
from sqlalchemy.orm import registry

from stock_port.domain.models import OrderView, Order, BatchLine, Supplier

mapper_registry = registry()
metadata = mapper_registry.metadata

supplier_table = Table(
    "suppliers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("name", String, nullable=False),
    Column("phone_number", String(11), nullable=False, unique=True),
)

batch_line_table = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("order_id", ForeignKey("orders.id"), nullable=False),
    Column("batch_ref", String, nullable=False, unique=True),
    Column("expected_quantity", Integer, nullable=False),
    Column("delivered_quantity", Integer, nullable=True),
    Column("delivery_date", DateTime, nullable=True),
    Column("cost", Float, nullable=False),
)

order_table = Table(
    "orders",
    metadata,
    Column("id", String, primary_key=True),
    Column("shop_id", String, nullable=False),
    Column("order_date", DateTime, nullable=False),
    Column("expected_delivery_date", DateTime, nullable=False),
    Column("supplier_id", ForeignKey("suppliers.id"), nullable=False),
)


order_view_table = Table(
    "order_view",
    metadata,
    Column("shop_id", String, nullable=False),
    Column("order_id", String),
    Column("sku", String),
    Column("expected_delivery_date", DateTime),
    Column("expected_quantity", Integer),
    Column("delivery_date", DateTime, nullable=True),
    Column("delivered_quantity", Integer, nullable=True),
    Column("cost", Float),
    Column("status", String),
    Column("supplier", String),
    Column("supplier_phone", String),
)


def start_mappers():
    mapper_registry.map_imperatively(OrderView, order_view_table)
    mapper_registry.map_imperatively(Supplier, supplier_table)
    mapper_registry.map_imperatively(BatchLine, batch_line_table)
    mapper_registry.map_imperatively(
        Order,
        order_table,
        properties={
            "batch_line": Relationship(
                BatchLine, primary_join="and_(Order.id == batch_line_table.c.order_id)"
            ),
            "supplier": Relationship(
                Supplier,
                primary_join="and_(order_table.c.supplier_id == supplier_table.c.id)",
            ),
        },
    )
