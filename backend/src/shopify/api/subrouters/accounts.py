from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from shopify.domain import commands
from shopify import exceptions
from shopify.api import models
from shopify.api import utils
from shopify.api import bus

from shopify.api.dependencies import SessionDep
from shopify.api.dependencies import ActiveUserDep

router = APIRouter(prefix="/accounts", tags=["Accounts"])

# perform all authentication here


def get_access_token(email: str, password: str, session):
    user = utils.authenticate_user(session, email, password)
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
    return models.Token(access_token=access_token, token_type="bearer")


@router.post("/register/", status_code=201)
async def register(account: models.AccountCreate):
    cmd = commands.CreateAccount(**account.model_dump())
    try:
        bus.handle(cmd)
    except exceptions.EmailAlreadyRegistered:
        raise HTTPException(status_code=400, detail="Email Already Registered")
    except Exception as e:
        print(e.__class__)
        raise HTTPException(status_code=400, detail=f"{e}")
    return {"message": f"Verification link has been sent to {cmd.email}"}


@router.get("/verification/{token}", status_code=200)
async def verify(token: str):
    cmd = commands.VerifyAccount(verification_str=token)
    try:
        bus.handle(cmd)
    except exceptions.VerificationError as err:
        raise HTTPException(status_code=400, detail=f"Verification Error : {err}")
    except Exception as e:
        print(e.__class__)
        raise HTTPException(status_code=400, detail=f"{e}")
    return {"message": f"Verification successful"}


@router.post("/token")
async def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> models.Token:
    token = get_access_token(form_data.username, form_data.password, session)
    return token


@router.post("/auth")
async def login_for_token(session: SessionDep, login: models.Login) -> models.Token:
    token = get_access_token(login.email, login.password, session)
    return token


@router.get("/profile")
async def user_profile(active_user: ActiveUserDep):
    return models.Profile(**active_user)


async def logout():
    pass


async def update():
    pass


async def password_change():
    pass
