from datetime import datetime, timedelta
import uuid

from sqlmodel import Session
import pytz
import jwt

from shopify.db.models import Token
from shopify import config


class Tokenizer:
    def __init__(self, session: Session, events: list = []):
        self.session = session
        self.events = events

    def create(
        self, email: str, permissions: list[str], business_id: uuid, shop_id: uuid
    ):
        current_time = datetime.now(config.TIMEZONE)
        expiry_time = current_time + timedelta(
            seconds=config.INVITE_TOKEN_EXPIRATION_SECONDS
        )
        payload = {
            "permissions": permissions,
            "location": shop_uid,
            "target": business_id,
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
        token = Token(email, token_str, business_id, shop_id)
        self.events.append(
            events.CreatedManagerInviteToken(email, business_id, shop_id, token_str)
        )
        self.session.add(token)
        return token

    def get(token_str: str):
        token = self.session.exec(
            select(Token).where(Token.token_str == token_str)
        ).first()
        if (token is None) or (not token.is_valid):
            return None
        try:
            decoded_token = jwt.decode(
                token_str,
                config.get_secret_key(),
                algorithm=config.get_token_algorithm(),
            )
        except (jwt.ExpiredSignatureError, InvalidTokenError):
            token.is_valid = False
            return None
        else:
            token.decoded = decode_token
            return token
