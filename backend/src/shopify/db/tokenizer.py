from datetime import datetime, timedelta
import uuid

from sqlmodel import Session, select
import pytz
import jwt

from shopify.db.models import Token
from shopify.domain import events
from shopify import config


class Tokenizer:
    def __init__(self, session: Session, events: list = []):
        self.session = session
        self.events = events

    def create(
        self,
        email: str,
        permissions: list[str],
        business_id: uuid,
        shop_id: uuid,
        business_name: str,
        shop_location: str,
    ):
        existing_token = self.session.exec(
            select(Token).where(Token.shop_id == shop_id, Token.email == email)
        ).first()
        if existing_token and existing_token.is_valid:
            return existing_token.token_str
        current_time = datetime.now(config.TIMEZONE)
        expiry_time = current_time + timedelta(
            seconds=config.INVITE_TOKEN_EXPIRATION_SECONDS
        )
        payload = {
            "permissions": permissions,
            "location": str(shop_id),
            "target": str(business_id),
            "sub": email,
            "iat": current_time.timestamp(),
            "exp": expiry_time,
            "type": "manager_invite",
        }
        token_str = jwt.encode(
            payload,
            key=config.SECRET_KEY,
            algorithm=config.TOKEN_ALGORITHM,
        )
        token = Token(
            email=email, token_str=token_str, business_id=business_id, shop_id=shop_id
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

    def get(self, token_str: str):
        token = self.session.exec(
            select(Token).where(Token.token_str == token_str)
        ).first()
        if (token is None) or (not token.is_valid):
            return None
        try:
            decoded_token = jwt.decode(
                token_str.strip(),
                config.SECRET_KEY,
                algorithms=config.TOKEN_ALGORITHM,
            )
        except jwt.ExpiredSignatureError:
            token.expired = True
            token.is_valid = False
        except Exception as e:
            token.is_valid = False
            # add exception to log
        finally:
            if token.is_valid:
                data = token.model_dump()
                data.update({"decoded": decoded_token})
                return Token(**data)
            return token

    def fetch(self, business_id: uuid.UUID):
        invites = self.session.exec(
            select(Token).where(Token.business_id == business_id)
        ).all()
        return invites

    def get_shop_invite(self, shop_id: uuid.UUID):
        invite = self.session.exec(
            select(Token).where(Token.shop_id == shop_id, Token.is_valid == True)
        ).first()
        return invite
