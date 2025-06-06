from __future__ import annotations
from typing import Annotated, Any
import uuid

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from jwt.exceptions import InvalidTokenError
from sqlmodel import Session
import jwt

from shopify.api import utils
from shopify import views
from shopify import config
from shopify import db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/accounts/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(db.db_session)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[config.TOKEN_ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = utils.get_account_record(email, session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)]
):
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive User")
    if not current_user.get("is_verified"):
        raise HTTPException(status_code=400, detail="Unverified User")
    return current_user


## Business Related Dependencies
def get_business_id_from_user_record(
    business_name: str,
    active_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
):
    if business_name in active_user["business"]:
        return active_user["business"][business_name]["id"]
    raise HTTPException(status_code=404, detail="Business Not Found")


async def verify_current_user_is_business_owner(
    business_name: str,
    active_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
):
    if business_name in active_user["business"]:
        return active_user
    raise HTTPException(status_code=404, detail="Business Not Found")


async def verify_shop_belongs_to_current_user_business(
    business_name: str,
    shop_location: str,
    active_user: Annotated[
        dict[str, Any], Depends(verify_current_user_is_business_owner)
    ],
    session: Annotated[Session, Depends(db.db_session)],
):
    business = active_user["business"].get(business_name)
    if shop_location in business["shops"]:
        return active_user
    raise HTTPException(status_code=404, detail="Shop Not Found")


def get_shop_id_from_business_record(
    business_name: str,
    shop_location: str,
    business_owner: Annotated[
        dict[str, Any], Depends(verify_current_user_is_business_owner)
    ],
):
    business = business_owner["business"][business_name]
    if shop_location not in business["shops"]:
        raise HTTPException(status_code=404, detail="Shop Not Found")
    return business["shops"][shop_location]


SessionDep = Annotated[Session, Depends(db.db_session)]
ActiveUserDep = Annotated[dict[str, Any], Depends(get_current_active_user)]
BusinessIDDep = Annotated[uuid.UUID, Depends(get_business_id_from_user_record)]
ShopIDDep = Annotated[uuid.UUID, Depends(get_shop_id_from_business_record)]
