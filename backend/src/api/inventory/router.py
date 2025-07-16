import asyncio

from fastapi import APIRouter, Depends, HTTPException

from inventory.domain import commands
from inventory import exceptions
from inventory import views

from api.inventory import bus
from api.inventory import models
from api.shared_dependencies import ShopIDDep
from api.shared_dependencies import get_user_shop_association
from api.shared_dependencies import permission_checker_factory

router = APIRouter(
    prefix="/{business_name}/{shop_location}/inventory",
    tags=["Inventory"],
    dependencies=[
        Depends(
            get_user_shop_association
        )  # throws a not found if user has no association with shop
    ],
)

requires_permission = permission_checker_factory("inventory")


@router.get("/", response_model=models.ShopView)
async def inventory_view(shop_id: ShopIDDep):
    view = await views.get_inventory_view(shop_id)
    if view:
        return view
    raise HTTPException(status_code=404, detail="Inventory Is Empty Or Does Not Exist")


@router.get("/{sku}", response_model=models.StockView)
async def view_stock(shop_id: ShopIDDep, sku: str):
    view = await views.get_stock_view(shop_id=shop_id, sku=sku)
    if view:
        return view
    raise HTTPException(status_code=404, detail="Stock Does Not Exist")


@router.get("/{sku}/history", response_model=models.StockAudit)
async def view_stock_history(shop_id: ShopIDDep, sku):
    view = await views.get_stock_history(shop_id, sku)
    if view:
        return view
    raise HTTPException(status_code=404, detail="Stock Does Not Exist")


@router.get("/{sku}/batch/{batch_ref}", response_model=models.BatchAudit)
async def view_batch(shop_id: ShopIDDep, sku: str, batch_ref: str):
    view = await views.get_batch_history(shop_id, sku, batch_ref)
    if view:
        return view
    raise HTTPException(status_code=404, detail="Stock Or Batch Does Not Exist")


# requires can_add_new_product permissions
@router.post("/add")
# @requires_permission("can_add_new_product")
def add_stock(shop_id: ShopIDDep, stock: models.CreateStock):
    """
    Creates a new product in inventory.
    Requires `can_add_new_product` permission
    """
    command = commands.CreateStock(
        shop_id=shop_id, name=stock.name, quantity=stock.quantity, price=stock.price
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
# @requires_permission("can_delete_product")
def delete_stock(shop_id: ShopIDDep, sku: str):
    """
    Delete a product record from inventory.
    Requires permission `can_delete_product`
    """
    command = commands.DeleteStock(shop_id=shop_id, sku=sku)
    try:
        bus.handle(command)
    except exceptions.StockNotFound:
        raise HTTPException(
            status_code=400, detail=f"{sku} does not exists in shop inventory."
        )
    return {"message": "Stock deleted"}
