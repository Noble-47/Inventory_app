import uuid

from fastapi import APIRouter, Depends, Request, Response

from shopify.domain import commands
from shopify import views

from api.shopify import models
from api.shopify import bus
from api.shopify.dependencies import SessionDep, ShopIDDep, BusinessIDDep
from api.shopify.dependencies import verify_shop_belongs_to_current_user_business

router = APIRouter(
    prefix="/{business_name}",
    tags=["Shop"],
    dependencies=[Depends(verify_shop_belongs_to_current_user_business)],
)

# Unused business_id param is used to declare the type for the business_id in global prefix


# @router.get("/{shop_location}/profile", response_model=models.Shop)
# async def shop_profile(shop_id: ShopIDDep):
#    view = views.shop_view(shop_id)
#    return view


@router.get("/{shop_location}/settings", response_model=models.ShopSetting)
async def shop_settings(shop_id: ShopIDDep):
    view = views.shop_settings(shop_id)
    return view


@router.post("/{shop_location}/settings")
async def setup_shop(shop_id: ShopIDDep, settings: list[models.SettingIn]):
    for setting in settings:
        cmd = commands.UpdateSetting(entity_id=shop_id, name=name, value=value)
        bus.handle(cmd)


@router.post("/{shop_location}/create-manager-invite-link")
async def create_manager_invite_link(
    business_id: BusinessIDDep,
    shop_id: ShopIDDep,
    token_params: models.CreateInviteToken,
    request: Request,
):
    cmd = commands.CreateAssignmentToken(
        business_id=business_id,
        shop_id=shop_id,
        email=token_params.email,
        permissions=token_params.permissions,
    )
    bus.handle(cmd)
    return {
        "message": f"Invitation Sent To {token_params.email}",
        "token_url": request.url_for(
            "invite",
            shop_location=request.path_params["shop_location"],
            business_name=request.path_params["business_name"],
        )._url,
    }


@router.get("/{shop_location}/invite")
def invite(shop_id: ShopIDDep):
    view = views.shop_invite(shop_id)
    if view is None:
        return {}  # Response(status_code=204, content= "Shop Has No Valid Invite")
    return models.ShopInvite(**view)


@router.post("/{shop_location}/invite/delete")
def delete_invite(shop_id: ShopIDDep):
    pass


@router.post("/{shop_location}/invite/update")
def update_invite(shop_id: ShopIDDep):
    pass


@router.post("/{shop_location}/dismiss-manager")
async def dismiss_manager(business_id: BusinessIDDep, shop_id: ShopIDDep):
    cmd = commands.DismissManager(business_id=business_id, shop_id=shop_id)
    bus.handle(cmd)
