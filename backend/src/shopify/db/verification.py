from datetime import datetime, timedelta
from sqlmodel import Session, select
import jwt

from shopify.db.models import AccountVerification
from shopify import config


class AccountVerifier:

    def __init__(self, session: Session, events: list = []):
        self.session = session
        self.events = events

    def create(self, email: str):
        current_time = datetime.now(config.TIMEZONE)
        expiry_time = current_time + timedelta(
            days=config.VERIFICATION_TOKEN_EXPIRATION_SECONDS
        )
        payload = {
            "sub": email,
            "iat": current_time.timestamp(),
            "exp": expiry_time,
            "type": "account_verification",
        }

        verification_str = jwt.encode(
            payload, key=config.SECRET_KEY, algorithm=config.TOKEN_ALGORITHM
        )

        verification = AccountVerification(email, verification_str)
        self.events.append(events.VerificationTokenCreated(email, verification_str))
        return verification

    def get(verification_str: str):
        verification = self.session.exec(
            select(AccountVerification).where(
                AccountVerification.verification_str == verification_str
            )
        ).first()

        if verification is None or not (verification.is_valid):
            return None
        try:
            decoded = jwt.decode(
                verification_str, config.SECRET_KEY, algorithm=config.TOKEN_ALGORITHM
            )
        except (jwt.ExpiredSignatureError, InvalidTokenError):
            verification.is_valid = False
            return None
        else:
            verification.decoded = decoded
            return None
