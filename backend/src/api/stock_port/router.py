from uuid import UUID

from fastapi import APIRouter, Depends

from stock_port import views

from api.stock_port import models
from api.shopify.dependencies import get_user_shop_association
from api.shared_dependencies import ShopIDDep

router = APIRouter(
    prefix="/{business_name}/{shop_name}/orders",
    tags=["Order"],
    dependencies=[Depends(get_user_shop_association)],
)


@router.get("/", response_model=models.ShopOrders)
def view_supplies(shop_id: ShopIDDep):
    return views.get_shop_orders(shop_id)


@router.get("/{order_id}", response_model=models.Order)
def view_order_line(shop_id: ShopIDDep, order_id: UUID):
    return views.get_order_details(shop_id, order_id)


@router.post("/{order_id}/cancel")
def cancel_order(shop_id: ShopIDDep, cancel_order: models.CancelOrder):
    pass


@router.get("/suppliers", response_model=models.ShopSuppliers)
def view_shop_suppliers(shop_id: ShopIDDep):
    return views.get_suppliers(shop_id)


@router.get("/suppliers/{supplier_id}", response_model=models.Supplier)
def view_supplier_detail(shop_id: ShopIDDep, supplier_id: int):
    return views.get_supplier_detail(shop_id, supplier_id)


@router.post("/create")
def create_new_order(shop_id: ShopIDDep, order: models.Order):
    pass


@router.post("/complete-order")
def complete_order(shop_id: ShopIDDep, order: models.Order):
    pass
