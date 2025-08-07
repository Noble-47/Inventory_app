from datetime import datetime
from uuid import UUID
from typing import Any

from pydantic import BaseModel, Field

from stock_port.domain.commands import OrderedProducts, Delivery


class CancelOrder(BaseModel):
    order_id: UUID
    reason: str | None = Field(default=None)


class CreateOrder(BaseModel):
    supplier_firstname: str
    supplier_lastname: str
    supplier_phone: str
    orderline: list[OrderedProducts]
    expected_delivery_date: datetime


class OrderLine(BaseModel):
    sku: str
    expected_quantity: int
    delivered_quantity: int | None = Field(default=None)
    cost: float
    delivery_date: datetime | None = Field(default=None)


class Order(BaseModel):
    supplier_firstname: str
    supplier_lastname: str
    supplier_phone: str
    orderline: list[OrderLine]
    expected_delivery_date: datetime
    delivery_date: datetime | None = Field(default=None)
    status: str
    cost: float

Class DeliveryLine(BaseModel):
    sku:str
    quantity:str
    cost:float | None = Field(default=None)

class ProcessDelivery(BaseModel):
    order_id: UUID
    orderline: list[DeliveryLine]
    #orderline: dict[str, dict[str, Any]] = Field(
    #    description="Use this to pass in the quantity delivered as well as other info like 'cost' if need. the key must be the product sku and the value a dictionary with keywords `quantity`, `cost` and their respective values"
    #)

    #model_config = {
    #    "json_schema_extra": {
    #        "examples": [
    #            {
    #                "order_id": "",
    #                "orderline": {"product-sku": {"quantity": 12, "cost": ""}},
    #            }
    #        ]
    #   }
    #}


class OrderSlim(BaseModel):
    order_id: UUID = Field(validation_alias="id")
    supplier: str
    supplier_phone: str
    status: str
    expected_delivery_date: datetime


class ShopOrders(BaseModel):
    shop_id: UUID
    orders: list[OrderSlim]


class SupplierSlim(BaseModel):
    id: int
    firstname: str
    lastname: str
    phone: str


class Supplier(SupplierSlim):
    supplies: list[OrderSlim]


class ShopSuppliers(BaseModel):
    shop_id: UUID
    suppliers: list[SupplierSlim]


class Log(BaseModel):
    audit_id: int = Field(validation_alias="id")
    order_id: UUID = Field()
    description: str
    time: datetime
    payload: dict[str, Any]


class ShopHistory(BaseModel):
    shop_id: UUID
    logs: list[Log]
