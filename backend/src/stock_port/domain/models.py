from datetime import datetime
from pydantic import BaseModel


class Supplier(BaseModel):
    name: str
    phone_number: str


class OrderStatus(Enum, str):
    pending = "pending"
    delivered = "delivered"
    cancelled = "cancelled"


class BatchLine(BaseModel):
    order_id: uuid.UUID
    sku: str
    batch_ref: str
    expected_quantity: int
    delivered_quantity: int
    delivery_date: datetime
    cost: float


class Order(BaseModel):
    id: UUID
    shop_id: UUID
    order_date: datetime
    status: str
    batch_line = list[BatchLine]
    expected_delivery_date: datetime
    supplier: Supplier

    def mark_as_delivered(self):
        pass

    def cancel(self):
        pass


# Read Models
class SupplyView(BaseModel):
    ref: str
    shop_id: UUID
    order_id: UUID
    sku: str
    expected_delivery_date: datetime
    expected_quantity: int
    delivered_quantity: int
    delivery_date: datetime
    cost: float
    status: str
    supplier: str
    supplier_phone: str
