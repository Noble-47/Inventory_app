from typing import Annotated

from fastapi import APIRouter, Depends, Query

from api.debt_tracker import models
from api.shared_dependencies import get_user_shop_association, ShopIDDep

router = APIRouter(
    prefix="/{business_name}/{shop_location}",
    dependencies=[Depends(get_user_shop_association)],
    tags=["Tracker"],
)


@router.get("/debt_tracker/{purchase_ref}", response_model=models.DebtModel)
def get_debt_details(shop_id: ShopIDDep, ref: str):
    pass


@router.get("/debt_tracker/list", response_model=models.DebtorList)
def view_debtors_list(shop_id: ShopIDDep, query: Annotated[models.DebtQueryParams, Query(), None]=None):
    return views.fetch_debtors(shop_id, query)


# can clear customer debt
@router.delete("/debt_tracker/{ref}/clear")
def clear_debt(shop_id: ShopIDDep, ref: str):
    pass


# can add debt
@router.post("/debt_tracker/add")
def create_debt(shop_id: ShopIDDep, debt: models.DebtModel):
    pass
