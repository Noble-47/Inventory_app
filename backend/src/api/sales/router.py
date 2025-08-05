from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from sales.handlers import handle
from sales.domain import commands
from sales import views

from api.sales import models
from api.sales.dependencies import ProductRecord, ShopIDDep
from api.shared_dependencies import get_user_shop_association
from api.sales.dependencies import verify_products_can_be_dispatched

router = APIRouter(
    prefix="/{business_name}/{shop_location}/sale",
    dependencies=[Depends(get_user_shop_association)],
    tags=["Sales"],
)


@router.get("/list")
def view_shop_sales(
    shop_id: ShopIDDep, query: Annotated[models.SaleQueryParams, Query(), None] = None
) -> models.SaleList:
    view = views.fetch_sales(shop_id, query)
    if view:
        return models.SaleList(**view)
    return {}


@router.get("/history")
def view_sale_histry(shop_id: ShopIDDep) -> models.SaleLogs:
    view = views.get_sale_history(shop_id)
    if view:
        return models.SaleLogs(**view)
    return {}


@router.get("/{ref}")
def view_sale_detail(shop_id: ShopIDDep, ref: UUID) -> models.SaleRead:
    view = views.get_sale_detail(shop_id, ref)
    if view:
        return models.SaleRead(**view)
    return {}


@router.post("/", dependencies=[Depends(verify_products_can_be_dispatched)])
def create_new_sale(
    shop_id: ShopIDDep, sale: models.SaleWrite, product_record: ProductRecord
):
    command = commands.CreateSale(
        shop_id=shop_id,
        phone_number=sale.phone_number,
        firstname=sale.firstname,
        lastname=sale.lastname,
        products=[unit.model_dump() for unit in sale.units],
        selling_price=sale.selling_price,
        amount_paid=sale.amount_paid,
        inventory_record=product_record,
    )
    handle(command)
    return {"message": "sale record saved"}


# can delete sale
@router.delete("/{ref}")
def delete_sale_record(shop_id: ShopIDDep, ref: str):
    command = commands.DeleteSale(shop_id=shop_id, ref=reg)
    handle(command)
    return {"message": "sale record saved"}


# can update sale
@router.patch("/{ref}", dependencies=[Depends(verify_products_can_be_dispatched)])
def update_sale_record(shop_id: ShopIDDep, sale: models.Sale):
    updates = sale.dump_model()
    ref = updates.pop("ref")
    command = commands.UpdateSale(shop_id=shop_id, ref=ref, updates=updates)
    handle(command)
