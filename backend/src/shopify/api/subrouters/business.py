import uuid

from fastapi import APIRouter, Depends

from shopify.domain import commands
from shopify.api import models
from shopify.api import bus
from shopify import views

from shopify.api.dependencies import SessionDep, ActiveUserDep
from shopify.api.dependencies import verify_current_user_is_business_owner

router = APIRouter(
    prefix="/business",
    tags=["Business"],
    dependencies=[Depends(verify_current_user_is_business_owner)],
)


@router.get("/{business_id}/profile", response_model=models.BusinessProfile)
async def business_profile(business_id: uuid.UUID):
    business_view = views.business_view(business_id)
    return business_view


@router.get("/{business_id}/settings", response_model=models.BusinessSetting)
async def business_settings(business_id: uuid.UUID):
    setting_view = views.business_settings(business_id)
    return setting_view


@router.get("/{business_id}/invites", response_model=models.BusinessInvite)
async def business_invites(business_id: uuid.UUID):
    invite_view = views.business_invites(business_id)
    return invite_view


@router.get("/{business_id}/timeline", response_model=models.BusinessTimeLine)
async def business_timeline(business_id: uuid.UUID):
    timeline_view = view.business_timeline(business_id)
    return timeline_view


@router.get("/{business_id}/audit/{audit_id}", response_model=models.AuditDetails)
async def business_audit_timeline(business_: uuid.UUID, audit_id: int):
    unit_time_view = views.audit_unit(business_id, audit_id)
    return unit_time_view


@router.post("/{business_id}/settings", status_code=201)
async def setup_business(business_id: uuid.UUID, setting: list[models.Setting]):
    for setting in settings:
        cmd = commands.UpdateSetting(business_id, name, value)
        bus.handle(cmd)


@router.post("/{business_id}/add-shop", status_code=201)
async def add_shop(shop: models.ShopAdd, business_id: uuid.UUID):
    cmd = commands.AddShop(business_id, shop.location)
    bus.handle(cmd)


@router.post("/{business_id}/delete-shop", status_code=204)
async def remove_shop(shop: models.ShopRemove, business_id: uuid.UUID):
    cmd = commands.RemoveShop(business_id, shop.shop_id)
    bus.handle(cmd)
