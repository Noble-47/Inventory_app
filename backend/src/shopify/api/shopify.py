from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer

from shopify.api.dependencies import get_current_active_user
from shopify.api.subrouters import accounts
from shopify.api.subrouters import business
from shopify.api.subrouters import shops
from shopify.api import bus
from shopify import db

# Use Router
app = FastAPI(title="Inventra API")


app.include_router(accounts.router)
app.include_router(business.router)
app.include_router(shops.router)


@app.on_event("startup")
def on_startup():
    db.create_tables()

@app.post("business/create", status_code=201, tags=['Business'], dependencies=[Depends(get_current_active_user)])
async def create_business(business_name: str):
    owner_id = acctive_user['account_id']
    cmd = commands.CreateBusiness(business_name, owner_id)
    bus.handler(cmd)

@app.post(
    "/shop/manager/{token:str}",
    tags=['Manager'],
    description="Create manager unverified account"
)
async def create_manager(token:str):
    pass


