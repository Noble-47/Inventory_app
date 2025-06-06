import uuid

from fastapi import APIRouter, Depends, HTTPException

from shopify.domain import commands
from shopify.api import models
from shopify.api import bus
from shopify import views

from shopify.api.dependencies import SessionDep, ActiveUserDep, BusinessIDDep
from shopify.api.dependencies import verify_current_user_is_business_owner

router = APIRouter(
    tags=["Business"],
    dependencies=[Depends(verify_current_user_is_business_owner)],
)


@router.get("/{business_name}/profile", response_model=models.BusinessProfile)
async def business_profile(business_name: str, business_id: BusinessIDDep):
    business_view = views.business_view(business_id)
    if business_view is None:
        raise HTTPException(status_code=404, detail="Not Found")
    return business_view


@router.get("/{business_name}/settings", response_model=models.BusinessSetting)
async def business_settings(business_id: BusinessIDDep):
    setting_view = views.business_settings(business_id)
    return setting_view


@router.get("/{business_name}/invites", response_model=models.BusinessInvite)
async def business_invites(business_id: BusinessIDDep):
    invite_view = views.business_invites(business_id)
    return invite_view


@router.get("/{business_name}/timeline", response_model=models.BusinessTimeLine)
async def business_timeline(business_id: BusinessIDDep):
    timeline_view = views.business_timeline(business_id)
    return timeline_view


@router.get("/{business_name}/audit/{audit_id}", response_model=models.AuditDetails)
async def business_audit_timeline(business_id: BusinessIDDep, audit_id: int):
    unit_time_view = views.audit_unit(business_id, audit_id)
    return unit_time_view


@router.post("/{business_name}/settings", status_code=201)
async def setup_business(business_id: BusinessIDDep, settings: list[models.SettingIn]):
    for setting in settings:
        cmd = commands.UpdateSetting(
            entity_id=business_id, name=setting.name, value=setting.value
        )
        bus.handle(cmd)
    return {"message": "Settings Updated"}


@router.post("/{business_name}/add-shop", status_code=201)
async def add_shop(shop: models.ShopAdd, business_id: BusinessIDDep):
    cmd = commands.AddShop(business_id=business_id, location=shop.location)
    try:
        bus.handle(cmd)
    except exceptions.DuplicateShopRecord:
        return HTTPException(status_code=400, detail="Duplicate Shop")
    return {"message": f"New Shop Created : {cmd.location}"}


@router.post("/{business_name}/delete-shop", status_code=204)
async def remove_shop(shop: models.ShopRemove, business_id: BusinessIDDep):
    cmd = commands.RemoveShop(business_id=business_id, shop_id=shop.shop_id)
    bus.handle(cmd)
    return {"message": f"Delete Shop : {cmd.shop_id}"}
