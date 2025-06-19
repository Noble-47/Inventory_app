from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session
import jwt

from shopify.api import models as api_models
from shopify.utils import verify_password
from shopify.domain import models
from shopify import permissions
from shopify import config
from shopify import db


def authenticate_user(session, email: str, password: str):
    user_db = db.Account(session)
    user = user_db.get(email)
    if user is None or not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(config.TIMEZONE) + timedelta(
        seconds=config.API_TOKEN_EXPIRATION_SECONDS
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.SECRET_KEY, algorithm=config.TOKEN_ALGORITHM
    )
    return encoded_jwt


profile = {
    "firstname": "somename",
    "lastname": "somename",
    "email": "somename",
    "business": {
        "abc-sfs-345": {
            "name": "business_name",
            "shops": ["shop_1.id", "shop_2.id", "shop_3.id"],
            "created": "datetime",
        }
    },
    "managed_shops": {
        "bsf-asd-3242-dsdf": {
            "loc": "some location",
            "permissions": {"sale": [], "inventory": []},
        }
    },
}


def get_account_record(email: str, session: Session):
    accounts_db = db.Account(session)
    user = accounts_db.get(email)
    if user is None:
        return None
    registry_db = db.Registry(session)
    records = registry_db.fetch(user.id)
    records = parse_records(records)
    account_record = user.model_dump()
    account_record.update(records)
    return account_record


def parse_records(records: dict[str, list]):
    parsed = {}
    parsed["business"] = {}
    parsed["managed_shops"] = {}
    for business in records["business"]:
        parsed["business"].update(
            {
                business["business_name"]: {
                    "id": business["business_id"],
                    "shops": business["shops"],
                    "created": business["created"],
                }
            }
        )

    for shop in records["managed_shops"]:
        parsed["managed_shops"].update(
            {
                shop["location"]: {
                    "id": shop["shop_id"],
                    "permissions": permissions.parse_permission_str(
                        shop["permissions"]
                    ),
                    "assigned": shop["assigned"],
                }
            }
        )

    return parsed


def check_shop_belong_to_business(shop_id, business_id, session):
    shop_db = db.Shop(session)
    return shop_db.business_id == business_id
