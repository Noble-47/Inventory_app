from datetime import datetime
import uuid
import json

from sqlmodel import select

from shopify.domain.read_models import BusinessView, ShopView
from shopify.config import TIMEZONE
from shopify import db


def business_view(business_id: uuid.UUID):
    session = next(db.db_session())
    business = session.exec(
        select(BusinessView).where(BusinessView.business_id == business_id)
    ).first()
    if business is None:
        return
    shops = session.exec(
        select(ShopView).where(ShopView.business_id == business_id)
    ).all()
    view = business.model_dump()
    view["shops"] = [shop.model_dump() for shop in shops]
    return view


def shop_view(shop_id: uuid.UUID):
    session = next(db.db_session())
    shop = session.exec(select(ShopView).where(ShopView.shop_id == shop_id)).first()
    return shop.model_dump()


## view settings
def business_settings(business_id: uuid.UUID):
    session = next(db.db_session())
    setting_db = db.Setting(session)
    settings = setting_db.fetch(business_id)
    view = {}
    view["id"] = business_id
    view["shops"] = []
    view["settings"] = [
        {"name": setting.name, "value": setting.value, "tag": setting.tag, "description" : setting.description}
        for setting in settings
    ]
    shops = session.exec(
        select(ShopView.shop_id).where(ShopView.business_id == business_id)
    ).all()
    for shop_id in shops:
        shop_settings = setting_db.fetch(shop_id)
        view["shops"].append({
            "id": shop_id,
                "settings": [
                    {
                        "name": setting["name"],
                        "value": setting["value"],
                        "tag": setting["tag"],
                        "description" : setting["description"]
                    }
                    for setting in shop_settings
                ],
        })
    return view


def shop_settings(shop_id: uuid.UUID):
    session = next(db.db_session())
    setting_db = db.Setting(session)
    settings = setting_db.fetch(shop_id)
    view = {}
    view["id"] = shop_id
    view["settings"] = [
        {"name": setting.name, "value": setting.value, "tag": setting.tag, "description" : setting.description}
        for setting in settings
    ]
    return view


## view invites
def business_invites(business_id: uuid.UUID):
    session = next(db.db_session())
    token_db = db.Tokenizer(session)
    invites = token_db.fetch(business_id)
    view = {}
    view["id"] = business_id
    view["shops"] = [
        {
            "id": invite.shop_id,
            "invite": {
                "for": invite.email,
                "created": invite.created,
                "used": invite.used,
                "expired": invite.expired,
                "token" : invite.token_str
            },
        }
        for invite in invites
    ]
    return view

def shop_invite(shop_id:uuid.UUID):
    session = next(db.db_session())
    token_db = db.Tokenizer(session)
    invite = token_db.get_shop_invite(shop_id)
    if invite:
        return {
            'id' : shop_id,
            'invite' : {
                'for' : invite.email,
                'created' : invite.created,
                'used' : invite.used,
                'expired' : invite.expired,
                'token' : invite.token_str
            }
        }
    return None


## View history
def business_timeline(business_id: uuid.UUID):
    session = next(db.db_session())
    audit_db = db.Audit(session)
    timeline = audit_db.fetch(business_id)
    view = {"id": business_id}
    view["timeline"] = [
        {
            "audit_id": event.id,
            "name": event.name,
            "description": event.description,
            "time": datetime.fromtimestamp(event.time, tz=TIMEZONE),
        }
        for event in timeline
    ]
    return view


def audit_unit(business_id: uuid.UUID, audit_id):
    session = next(db.db_session())
    audit_db = db.Audit(session)
    audit = audit_db.get(audit_id, business_id)
    view = audit.model_dump()
    view['payload'] = json.loads(view['payload'])
    return view
