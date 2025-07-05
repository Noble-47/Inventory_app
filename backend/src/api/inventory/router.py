from fastapi import APIRouter, Depends

from inventory.domain import commands
from inventory import views

from api.inventory import bus
from api.inventory import models
from api.shared_dependencies import ShopIDDep
from api.shared_dependencies import get_user_shop_association

router = APIRouter(
    prefix="/{business_name}/{shop_name}/inventory",
    tags=["Inventory"],
    dependencies=[
        Depends(
            get_user_shop_association
        )  # throws a not found if user has no association with shop
    ],
)


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


@router.post("/add")
def add_stock(shop_id: ShopIDDep, stock: models.CreateStock):
    command = commands.CreateStock(
        shop_id=shop_id, name=stock.name, quantity=stock.quantity
    )
    try:
        bus.handle(command)
    except exceptions.DuplicateStock:
        raise HTTPException(
            status_code=400, detail=f"{name} already exists in shop inventory."
        )
    return {"message": "Stock added."}


@router.delete("/{sku}")
def delete_stock(shop_id: ShopIDDep, sku: str):
    commands = commands.DeleteStock(shop_id=shop_id, sku=stock.sku)
    try:
        bus.handle(command)
    except exceptions.StockNotFound:
        raise HTTPException(
            status_code=400, detail=f"{sku} does not exists in shop inventory."
        )
    return {"message": "Stock deleted"}
