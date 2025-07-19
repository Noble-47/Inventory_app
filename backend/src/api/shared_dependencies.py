from typing import Annotated, Any
from functools import wraps
import inspect
import uuid

from fastapi import Depends, HTTPException

from inventory.utils import verify_can_dispatch, verify_exists, get_stock_detail

from api.shopify.dependencies import get_user_shop_association


def get_shop_id_from_association_record(
    shop_location: str,
    record: Annotated[dict[str, Any], Depends(get_user_shop_association)],
):
    if record["shop_location"] == shop_location:
        return record["shop_id"]
    raise HTTPException(status=404, detail="Shop Not Found")


def get_stock_record(shop_id: str, sku: str):
    stock = get_stock_detail(shop_id, sku)
    if stock:
        return stock
    raise HTTPException(status_code=400, detail=f"No inventory record for SKU-{sku}")


def verify_stock_can_dispatch_products(shop_id: str, sku: str, quantity):
    if not verify_can_dispatch(shop_id=shop_id, sku=sku, quantity=quantity):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot dispatch product - {sku} - from shop, stock level is low",
        )


def verify_stock_exists(shop_id: str, sku: str):
    if not verify_exists(shop_id=shop_id, sku=sku):
        raise HTTPException(
            status_code=400, detail=f"SKU-{sku} was not found in shop inventory"
        )


def permission_checker_factory(service_name: str):
    def requires_permission(permission):
        def decorator_function(api_func):
            @wraps(api_func)
            def wrapper(
                record: Annotated[dict[str, Any], Depends(get_user_shop_association)],
                *args,
                **kwargs,
            ):
                print(record)
                if not permission in record["permissions"][service_name]:
                    raise HTTPException(status_code=405, detail="Not allowed")
                return api_func(*args, **kwargs)

            return wrapper

        return decorator_function

    return requires_permission


ShopIDDep = Annotated[uuid.UUID, Depends(get_shop_id_from_association_record)]
