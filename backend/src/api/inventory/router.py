from fastapi import APIRouter, Depends

from inventory.domain import commands
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
def inventory_view(shop_id: ShopIDDep):
    return views.get_inventory_view(shop_id)


@router.get("/{sku}", response_model=models.StockView)
def view_stock(shop_id: ShopIDDep, sku: str):
    return views.get_stock_view(shop_id, sku)


@router.get("/{sku}/history", response_model=models.StockAudit)
def view_stock_history(shop_id: ShopIDDep, sku):
    return views.get_stock_history(shop_id, sku)


@router.get("/{sku}/batch/{batch_ref}", response_model=models.BatchAudit)
def view_batch(shop_id: ShopIDDep, sku: str, batch_ref: str):
    return veiws.get_batch_history(shop_id, sku, batch_ref)


# requires can_add_new_product permissions
@router.post("/add")
@requires_permission("can_add_new_product")
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
    except exceptions.DuplicateStock:
        raise HTTPException(
            status_code=400, detail=f"{name} already exists in shop inventory."
        )
    return {"message": "Stock added."}


# requires can_delete_product
@router.delete("/{sku}")
@requires_permission("can_delete_product")
def delete_stock(shop_id: ShopIDDep, sku: str):
    """
    Delete a product record from inventory.
    Requires permission `can_delete_product`
    """
    commands = commands.DeleteStock(shop_id=shop_id, sku=stock.sku)
    try:
        bus.handle(command)
    except exceptions.StockNotFound:
        raise HTTPException(
            status_code=400, detail=f"{sku} does not exists in shop inventory."
        )
    return {"message": "Stock deleted"}
