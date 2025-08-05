from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from shopify.domain import commands
from shopify import views

from api.shopify import bus
from api.shopify.models import ManagerPermissions, Manager
from api.shopify.dependencies import BusinessIDDep, ShopIDDep
from api.shopify.dependencies import verify_current_user_is_business_owner


router = APIRouter(
    prefix="/{business_name}/managers",
    tags=["Manage Managers"],
    dependencies=[Depends(verify_current_user_is_business_owner)],
)


@router.get("/", response_model=list[Manager])
def get_managers_list(business_id: BusinessIDDep) -> list[Manager]:
    view = views.get_business_managers(business_id)
    return [Manager(**item) for item in view]


@router.delete("/{shop_location}/remove")
def dismiss_shop_manager(business_id: BusinessIDDep, shop_id: ShopIDDep):
    cmd = commands.DismissManager(business_id=business_id, shop_id=shop_id)
    bus.handle(cmd)
    return {"message": "Manager dismissed"}
