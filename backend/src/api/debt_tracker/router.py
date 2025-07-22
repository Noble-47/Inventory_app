from typing import Annotated
from fastapi import APIRouter, Depends, Query, Response, HTTPException

from debt_tracker import views
from debt_tracker.handlers import handle
from debt_tracker.domain import commands

from api.shared_dependencies import get_user_shop_association
from api.debt_tracker.dependencies import ShopIDDep
from api.debt_tracker import models

router = APIRouter(
    prefix="/{business_name}/{shop_location}",
    dependencies=[Depends(get_user_shop_association)],
    tags=["Tracker"],
)


@router.get("/debt_tracker/list", response_model=models.DebtorList)
def view_debtors_list(shop_id: ShopIDDep):
    debtors = views.get_debtors(shop_id)
    if debtors:
        return debtors
    return Response(content={}, status_code=200)


@router.get("/debt_tracker/{sale_ref}", response_model=models.DebtRead)
def get_debt_details(shop_id: ShopIDDep, sale_ref: str):
    debt = views.get_debt(shop_id, sale_ref=sale_ref)
    if debt:
        return debt
    raise HTTPException(status_code=404, detail=f"No debt record for {sale_ref}")


# can clear customer debt
@router.post("/debt_tracker/waive")
def clear_debt(shop_id: ShopIDDep, ref: str):
    cmd = commands.WaiveDebt(shop_id=shop_id, sale_ref=ref)
    try:
        handle(cmd)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    else:
        return {"message": "Debt waived off"}


# can add debt
@router.post("/debt_tracker/add")
def create_debt(shop_id: ShopIDDep, debt: models.DebtWrite):
    cmd = commands.RecordDebt(**debt.model_dump(), shop_id=shop_id)
    try:
        handle(cmd)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    else:
        return {"message": "Entry is being processed"}

@router.post("/debt_tracker/make-payment/")
def make_payment(shop_id: ShopIDDep, payment:models.Payment):
    cmd = commands.RecordPayment(**payment.model_dump(), shop_id=shop_id)
    #try:
    handle(cmd)
    #except:
    #    pass
    #else:
    #    return {"message" : "Payment recorded"}
