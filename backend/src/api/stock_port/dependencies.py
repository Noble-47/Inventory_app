from fastapi import Request, HTTPException

from inventory.utils import ensure_exists
from api.shared_dependencies import ShopIDDep


async def ensure_product_exists(shop_id: ShopIDDep, request: Request):
    order = await request.json()
    sku_set = set(product["sku"] for product in order["orderline"])
    for sku in sku_set:
        if not ensure_exists(shop_id=shop_id, sku=sku):
            raise HTTPException(status_code=400, detail=f"SKU-{sku} not recognized")
