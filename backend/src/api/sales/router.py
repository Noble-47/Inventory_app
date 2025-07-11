from fastapi import APIRouter, Depends

from api.sales import models
from api.shared_dependencies import get_user_shop_association, ShopIDDep

router = APIRouter(
    prefix="/{business_name}/{shop_location}/sale",
    dependencies=[Depends(get_user_shop_association)],
    tags=["Sales"],
)


@router.get("/list")
def view_shop_sales(shop_id: ShopIDDep, query: models.SaleQueryParams = None):
    return views.fetch_sales(shop_id, query)


@router.get("/{ref}")
def view_sale_detail(shop_id: ShopIDDep, ref: str):
    return views.get_sale_detail(shop_id, ref)


@router.post("/")
def create_new_sale(shop_id: ShopIDDep, sale: models.SaleModel):
    pass


# can delete sale
@router.delete("/{ref}")
def delete_sale_record(shop_id: ShopIDDep, ref: str):
    pass


# can update sale
@router.patch("/{ref}")
def update_sale_record(shop_id: ShopIDDep, sale: models.SaleModel):
    pass
