from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.security import OAuth2PasswordBearer

from shopify.bootstrap import bootstrap
from shopify.domain import commands
from shopify import permissions
from shopify import exceptions
from shopify import config
from shopify import db

from api.shopify.dependencies import ActiveUserDep
from api.shopify.models import InviteAccept, PermissionModel


bus = bootstrap()

def setup(app:FastAPI):

    from api.shopify.subrouters import shops
    from api.shopify.subrouters import accounts
    from api.shopify.subrouters import business

    app.include_router(accounts.router)
    app.include_router(business.router)
    app.include_router(shops.router)


    @app.on_event("startup")
    def on_startup():
        db.create_tables()

    @app.get("/shopify", tags=["Services"])
    def root():
        return "Shopify service is running"

    @app.post(
        "/business/create",
        status_code=201,
        tags=["Business"],
    )
    async def create_business(business_name: str, active_user: ActiveUserDep):
        user_email = active_user["email"]
        cmd = commands.CreateBusiness(name=business_name, email=user_email)
        try:
            bus.handle(cmd)
        except exceptions.DuplicateBusinessRecord as e:
            return HTTPException(status_code=400, detail=f"{e}")
        except exceptions.UnresolvedError:
            return HTTPException(status_code=500, detail="Something Unexpected Occurred.")
        return {"message": f"Business : {cmd.name} Created Successfully."}


    @app.post(
        "/shop/manager/accept/",
        tags=["Shop"],
        description="Create manager unverified account",
        status_code=201,
    )
    async def create_manager(invitee: InviteAccept):
        cmd = commands.CreateManager(
            firstname=invitee.firstname,
            lastname=invitee.lastname,
            email=invitee.email,
            token_str=invitee.token_str.strip(),
            password=invitee.password,
        )
        try:
            bus.handle(cmd)
        except (exceptions.ShopAlreadyHasManager, exceptions.ShopNotFound):
            return HTTPException(status_code=400, detail="Shop Invite Request Failed")
        except exceptions.InvalidInvite as err:
            return HTTPException(status_code=400, detail=str(err).title())
        except exceptions.UnresolvedError:
            return HTTPException(status_code=500, detail="Something Unexpected Occurred.")
        return {"message": "Invitation confirmed, Kindly check your email to proceed"}


    @app.get("/permissions/all", response_model=PermissionModel, tags=["Shop"])
    async def get_all_permissions():
        return permissions.ALL_PERMISSIONS
