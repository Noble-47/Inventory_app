from typing import Annotated
import json

from fastapi import Request, Depends, HTTPException

from api.shared_dependencies import (
    verify_stock_exists,
    verify_stock_can_dispatch_products,
)
from api.shared_dependencies import get_stock_record
from api.shared_dependencies import ShopIDDep


async def get_product_details(shop_id: ShopIDDep, request: Request):
    shop_id = str(shop_id)
    sale = await request.json()
    products = sale.get("units", [])
    stocks = {}
    for product in products:
        sku = product["product_sku"]
        stock = get_stock_record(shop_id=shop_id, sku=sku)
        stocks[sku] = stock
    return stocks


async def verify_products_can_be_dispatched(
    request: Request,
    product_record: Annotated[dict[str, dict], Depends(get_product_details)],
):
    sale = await request.json()
    products = sale.get("units", [])
    dispatch_errors = []
    for product in products:
        sku = product["product_sku"]
        quantity = product["quantity"]
        level = product_record[sku]["level"]
        if quantity > level:
            dispatch_errors.append(sku)
    if dispatch_errors:
        raise HTTPException(
            status_code=400, detail=f"Low stock level: {','.join(dispatch_errors)}"
        )


ProductRecord = Annotated[dict[str, dict], Depends(get_product_details)]
