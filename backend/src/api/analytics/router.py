from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException

from analytics import analytics
from api.analytics import models
from api.shared_dependencies import get_user_shop_association, ShopIDDep

router = APIRouter(
    prefix="/{business_name}/{shop_location}/analytics",
    dependencies=[Depends(get_user_shop_association)],
    tags=["Analytics"],
)


@router.get("/")
def view_shop_analytics(shop_id: ShopIDDep) -> models.AnalyticReport:
    return analytics.get_shop_analytics(shop_id)
