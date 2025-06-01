from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from pydantic import EmailStr

from shopify.domain import commands
from shopify.api import utils
from shopify.api import bus

from shopify.api.dependencies import SessionDep
from shopify.api.dependencies import get_current_active_user
from shopify.api.models import Profile, AccountCreate, Token

router = APIRouter(prefix="/accounts", tags=["Accounts"])

# perform all authentication here


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = utils.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = utils.create_access_token(data={"sub": user.email})
    # include account profile in response
    # account profile should contain registry showing account-entity associations
    # as profile types
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register/", status_code=201)
async def register(create_account: AccountCreate):
    cmd = command.CreateAccount(**account.model_dump())
    bus.handle(create_user)


@router.post("/verification/{token}")
async def verify(email: EmailStr, token_url: str):
    cmd = commands.VerifyAccount(email, token_str)
    bus.handle(cmd)


async def logout():
    pass


async def update():
    pass


async def password_change():
    pass
