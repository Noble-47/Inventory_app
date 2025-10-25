from collections import namedtuple, defaultdict
from datetime import datetime, timedelta
import hashlib
import uuid

from sqlmodel import Session, select
import pytz
import jwt

from shopify.db.models import Token
from shopify.domain import events
from shopify import triggers
from shopify import config


Shop = namedtuple("Shop", "shop_id, shop_location")


class Tokenizer:
    def __init__(self, session: Session, events: list = []):
        self.session = session
        self.events = events

    def create_token(self, email: str, timestamp):
        return hashlib.sha256(
            f"{email}:{timestamp}:{config.SECRET_KEY}".encode()
        ).hexdigest()[:10]

    def validate_email(self, email: str, token: Token):
        test_token = self.create_token(email, token.created)
        return test_token == token.token_str

    def create(
        self,
        email: str,
        permissions: list[str],
        business_id: uuid,
        shop_id: uuid,
        shop_location: str,
        business_name: str,
    ):
        existing_token = self.session.exec(
            select(Token).where(Token.shop_id == shop_id, Token.email == email)
        ).first()
        if existing_token and existing_token.is_valid:
            if existing_token.sent:
                return existing_token
            else:
                try:
                    triggers.send_invite_email(self.session, token=existing_token)
                finally:
                    return existing_token.token_str
        current_time = datetime.now(config.TIMEZONE).timestamp()
        token_str = self.create_token(email, current_time)
        token = Token(
            email=email,
            token_str=token_str,
            business_id=business_id,
            shop_id=shop_id,
            shop_location=shop_location,
            permissions=permissions,
            created=current_time,
        )
        self.events.append(
            events.CreatedManagerInviteToken(
                business_id=business_id,
                shop_id=shop_id,
                shop_location=shop_location,
                email=email,
                token_str=token_str,
            )
        )
        self.session.add(token)
        return token

    def delete(self, shop_id, email: str):
        token = self.session.exec(
            select(Token).where(Token.email == email, Token.shop_id == shop_id)
        ).first()
        if token:
            self.session.delete(token)
        else:
            raise exceptions.InvalidInvite()

    def get(self, token_str: str, email: str):
        token = self.session.exec(
            select(Token).where(Token.token_str == token_str)
        ).first()
        if (token is None) or (not token.is_valid):
            return None
        if not self.validate_email(email, token):
            return None
        return token

    def fetch(self, business_id: uuid.UUID):
        invites = self.session.exec(
            select(Token).where(Token.business_id == business_id)
        ).all()
        grouped = defaultdict(list)
        for invite in invites:
            shop = Shop(shop_id=invite.shop_id, shop_location=invite.shop_location)
            grouped[shop].append(invite)
        return list(grouped.items())

    def get_shop_invite(self, shop_id: uuid.UUID):
        invites = self.session.exec(
            select(Token).where(Token.shop_id == shop_id)  # , Token.is_valid == True)
        ).all()
        if invites:
            return invites[0].shop_location, invites
        return None, []

    def mark_as_sent(self, token_str: str):
        token = self.session.exec(
            select(Token).where(Token.token_str == token_str)
        ).first()
        token.sent = True
