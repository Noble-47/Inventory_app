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


def authenticate_account(session, email: str, password: str):
    db = db.Account(session)
    user = db.get(email)
    if user is None:
        return False
    if verify_password(password, user.password) is False:
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(config.TIMEZONE) + timedelta(
        seconds=config.API_TOKEN_EXPIRATION_SECONDS
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def get_account_record(email: str, session: Session):
    accounts_db = db.Account(session)
    user = accounts_db.get(email)
    if user is None:
        return None
    registry_db = db.Registry(session)
    records = registry_db.fetch(user.id)
    account_record = user.model_dump()
    account_record.pop("password_hash")
    registry, permissions = parse_user_registry(records)
    account_record["registry"] = registry
    account_record["permissions"] = permissions
    return account_record


def parse_user_registry(records: list[models.Registry]):
    parsed_permissions = {}
    registry = {}
    for record in records:
        parsed_permissions[record.entity_id] = permission.parse_permission_str(
            record.permission
        )
        registry[record.entity_id] = {
            "name": record_entity_name,
            "type": record.entity_type,
        }
    return registry, parsed_permissions

def check_shop_belong_to_business(shop_id, business_id, session):
    shop_db = db.Shop(session)
    return shop_db.business_id == business_id
