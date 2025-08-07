from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response

from stock_port.handlers import handle
from stock_port.domain import commands
from stock_port import exceptions
from stock_port import views

from api.stock_port import models
from api.shopify.dependencies import get_user_shop_association
from api.stock_port.dependencies import ensure_product_exists
from api.shared_dependencies import ShopIDDep

router = APIRouter(
    prefix="/{business_name}/{shop_location}/orders",
    tags=["Order"],
    dependencies=[Depends(get_user_shop_association)],
)


@router.get("/", response_model=models.ShopOrders)
def view_orders(shop_id: ShopIDDep):
    view = views.get_orders(shop_id)
    if view:
        return view
    raise HTTPException(status_code=404, detail="Shop record not found")


@router.get("/suppliers", response_model=models.ShopSuppliers)
def view_shop_suppliers(shop_id: ShopIDDep):
    view = views.get_suppliers(shop_id)
    if view:
        return view
    return Response(content={}, status_code=200)
    raise HTTPException(status_code=404, detail="Shop record not found")


@router.get("/suppliers/{supplier_id}", response_model=models.Supplier)
def view_supplier_detail(shop_id: ShopIDDep, supplier_id: int):
    view = views.get_supplier_details(shop_id, supplier_id)
    if view:
        return view
    return Response(content={}, status_code=200)


@router.get("/history", response_model=models.ShopHistory)
def view_order_history(shop_id: ShopIDDep):
    view = views.get_shop_history(shop_id)
    if view:
        return view
    return Response(content={}, status_code=200)


@router.get("/{order_id}", response_model=models.Order)
def view_order(shop_id: ShopIDDep, order_id: UUID):
    view = views.get_order_details(shop_id=shop_id, order_id=order_id)
    if view:
        return view
    return Response(content={}, status_code=200)


@router.post("/create")
def create_new_order(shop_id: ShopIDDep, order: models.CreateOrder):
    cmd = commands.CreateOrder(
        shop_id=shop_id,
        delivery_date=order.expected_delivery_date,
        firstname=order.supplier_firstname,
        lastname=order.supplier_lastname,
        phone=order.supplier_phone,
        orderline=order.orderline,
    )
    handle(cmd)
    return {"Message": "Order created"}


@router.post("/complete-order")
def process_delivery(shop_id: ShopIDDep, delivery: models.ProcessDelivery):
    orderline = dict(
        (d['sku'], {'quantity':d['quantity'], 'cost':d['cost']})
        for d in cmd.orderline
    )
    cmd = commands.ProcessDelivery(
        shop_id=shop_id,
        order_id=delivery.order_id,
        orderline=orderline,
    )
    try:
        handle(cmd)
    except exceptions.DuplicateOrderDelivery:
        raise HTTPException(
            status_code=400, detail="Order has already been marked as delivered"
        )
    except exceptions.UnprocessableDelivery:
        raise HTTPException(
            status_code=400,
            detail="Delivery cannot be processed, check the input fields",
        )
    except exceptions.CancelledOrder:
        raise HTTPException(status_code=400, detail="Order was previously cancelled")
    return {"Message": "Delivery is being processed"}


@router.post("/cancel")
def cancel_order(shop_id: ShopIDDep, cancel: models.CancelOrder):
    cmd = commands.CancelOrder(
        shop_id=shop_id, order_id=cancel.order_id, reason=cancel.reason
    )
    handle(cmd)

    return {"Message": "Order cancelled"}
