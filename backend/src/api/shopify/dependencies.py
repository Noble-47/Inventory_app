from __future__ import annotations
from typing import Annotated, Any
import uuid

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from jwt.exceptions import InvalidTokenError
from sqlmodel import Session
import jwt

from api.shopify import utils
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
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
):
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive User")
    if not current_user.get("is_verified"):
        raise HTTPException(status_code=400, detail="Unverified User")
    return current_user


## Business Related Dependencies


## Business Owners Dependencies
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
    if shop_location in business["shops"]:
        return business["shops"][shop_location]["id"]
    raise HTTPException(status_code=404, detail="Shop Not Found")


## Shop Managers Dependencies
def get_user_business_association(
    business_name: str,
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    session: Annotated[Session, Depends(db.db_session)],
):
    record = {
        "business_name": business_name,
        "association_type": "",
        "user_id": user["id"],
        "user_email": user["email"],
        "user_fullname": f"{user['firstname']} {user['lastname']}",
        "shops": [],
    }

    business_id = utils.get_business_id(business_name, session)
    if business_id is None:
        raise HTTPException(status_code=404, detail="Business Not Found.")
    if business_name in user["business"]:
        record["association_type"] = "business_owner"
        record["shops"] = user["business"][business_name]["shops"]

    elif business_name in user["manager_record"]:
        record["association_type"] = "shop_manager"
        reocrd["shops"] = user["manager_record"][business_name].keys()

    else:
        raise HTTPException(status_code=404, detail="Business Not Found.")

    record["business_id"] = business_id
    return record


def get_user_shop_association(
    business_name: str,
    shop_location: str,
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    session: Annotated[Session, Depends(db.db_session)],
):
    record = {
        "business_name": business_name,
        "shop_location": shop_location,
        "shop_id": "",
        "association_type": "",
        "permissions": "",
        # "user_id": user["id"],
        "user_email": user["email"],
        "user_fullname": f"{user['firstname']} {user['lastname']}",
    }

    business_id = utils.get_business_id(business_name, session)
    shop_id = utils.get_shop_id(
        business_id=business_id, shop_location=shop_location, session=session
    )
    if shop_id is None:
        raise HTTPException(detail="Shop Not Found.", status_code=404)
    if business_id is None:
        raise HTTPException(status_code=404, detail="Business Not Found.")
    record["shop_id"] = shop_id
    record["business_id"] = business_id

    if shop_location in user["business"].get(business_name, dict()):
        record["association_type"] = "business_owner"
        record["permissions"] = permissions.parse_permissions("*")
        return record

    if business_name not in user["manager_record"]:
        raise HTTPException(status_code=404, detail="Shop Not Found")

    if shop_location not in user["manager_record"][business_name]:
        raise HTTPException(status_code=404, detail="Shop Not Found")

    record["association_type"] = "shop_manager"
    permissions = user["manager_record"][business_id][shop_location]["permissions"]
    record["permissions"] = permissions
    return record


SessionDep = Annotated[Session, Depends(db.db_session)]
ActiveUserDep = Annotated[dict[str, Any], Depends(get_current_active_user)]
BusinessIDDep = Annotated[uuid.UUID, Depends(get_business_id_from_user_record)]
ShopIDDep = Annotated[uuid.UUID, Depends(get_shop_id_from_business_record)]
BusinessRecordDep = Annotated[dict[str, Any], Depends(get_user_business_association)]
ShopRecordDep = Annotated[dict[str, Any], Depends(get_user_shop_association)]
