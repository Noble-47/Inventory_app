from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.shopify.models import ManagerPermissions, Manager


from api.shopify.dependencies import verify_current_user_is_business_owner
from api.shopify.dependencies import BusinessIDDep


router = APIRouter(
    prefix="/{business_name}/managers",
    tags=["Manage Managers"],
    dependencies=[Depends(verify_current_user_is_business_owner)],
)


@router.get("/", response_model=list[Manager])
def get_managers_list(business_name: str):
    pass


@router.get("/{manager_id}", response_model=Manager)
def get_manager_details(business_name: str, manager_id: int):
    pass


@router.post("{manager_id}/permissions/update")
def update_manager_permission(business_name: str, manager_id: int):
    pass


@router.delete("{manager_id}/remove")
def dismiss_shop_manager(business_name: str, manager_id: int):
    pass
