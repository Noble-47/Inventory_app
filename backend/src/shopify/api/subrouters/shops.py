import uuid

from fastapi import APIRouter, Depends

from shopify.domain import commands
from shopify.api import models
from shopify.api import bus
from shopify import views

from shopify.api.dependencies import SessionDep
from shopify.api.dependencies import verify_shop_belongs_to_current_user_business

router = APIRouter(
    prefix="/{business_id}/shop",
    tags=["Shop"],
    dependencies=[Depends(verify_shop_belongs_to_current_user_business)],
)

# Unused business_id param is used to declare the type for the business_id in global prefix


@router.get("/{shop_id}/profile", response_model=models.Shop)
async def shop_profile(business_id: uuid.UUID, shop_id: uuid.UUID):
    view = views.shop_view(shop_id)
    return view


@router.get("/{shop_id}/settings", response_model=models.ShopSetting)
async def shop_settings(shop_id: uuid.UUID, business_id: uuid.UUID):
    view = views.shop_settings(shop_id)
    return view


@router.post("/{shop_id}/settings")
async def setup_shop(
    shop_id: uuid.UUID, business_id: uuid.UUID, settings: list[models.Setting]
):
    for setting in settings:
        cmd = commands.UpdateSetting(shop_id, name, value)
        bus.handle(cmd)


@router.post("/{shop_id}/create-manager-invite-link")
async def create_manager_invite_link(
    shop_id: uuid.UUID, business_id: uuid.UUID, token_params: models.CreateInviteToken
):
    cmd = commands.CreateAssignmentToken(
        business_id, shop_id, token_params.email, token_params.permissions
    )
    bus.handle(cmd)


@router.post("{shop_id}/dismiss-manager")
async def dismiss_manager(shop_id: uuid.UUID, business_id: uuid.UUID):
    cmd = commands.DismissManager(business_id, shop_id)
    bus.handle(cmd)
