import asyncio

from fastapi import APIRouter, Depends, HTTPException

from inventory.domain import commands
from inventory import exceptions
from inventory import views

from api.inventory import bus
from api.inventory import models
from api.shared_dependencies import ShopIDDep
from api.shared_dependencies import get_user_shop_association

router = APIRouter(
    prefix="/{business_name}/{shop_location}/inventory",
    tags=["Inventory"],
    dependencies=[
        Depends(
            get_user_shop_association
        )  # throws a not found if user has no association with shop
    ],
)


@router.get("/")
async def inventory_view(shop_id: ShopIDDep) -> models.ShopView:
    view = await views.get_inventory_view(shop_id)
    if view:
        return models.ShopView(**view)
    return {}


@router.get("/{sku}")
async def view_stock(shop_id: ShopIDDep, sku: str) -> models.StockView:
    view = await views.get_stock_view(shop_id=shop_id, sku=sku)
    if view:
        return models.StockView(**view)
    return {}


@router.get("/{sku}/history")
async def view_stock_history(shop_id: ShopIDDep, sku) -> models.StockAudit:
    view = await views.get_stock_history(shop_id=shop_id, sku=sku)
    if view:
        return models.StockAudit(**view)
    return {}


@router.get("/{sku}/batch/{batch_ref}")
async def view_batch(shop_id: ShopIDDep, sku: str, batch_ref: str) -> models.BatchAudit:
    view = await views.get_batch(shop_id, sku, batch_ref)
    if view:
        return models.BatchAudit(**view)
    return {}


@router.post("/add")
def add_stock(shop_id: ShopIDDep, stock: models.CreateStock):
    """
    Creates a new product in inventory.
    Requires `can_add_new_product` permission
    """
    command = commands.CreateStock(
        shop_id=shop_id,
        name=stock.name,
        quantity=stock.quantity,
        price=stock.price,
        brand=stock.brand,
        packet_size=stock.packet_size,
        packet_type=stock.packet_type,
    )
    try:
        bus.handle(command)
    except exceptions.DuplicateStockRecord:
        raise HTTPException(
            status_code=400, detail=f"{stock.name} already exists in shop inventory."
        )
    return {"message": "Stock added."}


# requires can_delete_product
@router.delete("/{sku}")
def delete_stock(shop_id: ShopIDDep, sku: str):
    """
    Delete a product record from inventory.
    Requires permission `can_delete_product`
    """
    command = commands.DeleteStock(shop_id=shop_id, sku=sku)
    print(shop_id)
    try:
        bus.handle(command)
    except exceptions.StockNotFound:
        raise HTTPException(
            status_code=400, detail=f"{sku} does not exists in shop inventory."
        )
    return {"message": "Stock deleted"}
