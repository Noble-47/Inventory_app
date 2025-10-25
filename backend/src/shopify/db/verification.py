from datetime import datetime, timedelta
from sqlmodel import Session, select
import jwt

from shopify.db.models import AccountVerification
from shopify.db import events
from shopify import config
from shopify import db


class AccountVerifier(db.BaseRepo):

    def __init__(self, session: Session, events: list = []):
        self.session = session
        self.events = events

    def _create(self, email: str):
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

        verification = AccountVerification(
            email=email, verification_str=verification_str
        )
        self.events.append(
            events.VerificationTokenCreated(
                email=email, verification_str=verification_str
            )
        )
        return verification

    def _get(self, verification_str: str):
        verification = self.session.exec(
            select(AccountVerification).where(
                AccountVerification.verification_str == verification_str.strip()
            )
        ).first()

        if verification is None:
            return None
        try:
            decoded = jwt.decode(
                verification.verification_str,
                config.SECRET_KEY,
                algorithm=config.TOKEN_ALGORITHM,
            )
        except jwt.ExpiredSignatureError:
            verification.invalid_cause = "Expired Token"
        except jwt.InvalidTokenError:
            verification.invalid_cause = "Invalid Token"
        else:
            verification.decoded = decoded
        finally:
            if hasattr(verification, "invalid_cause"):
                verification.is_valid = False
                print(verification.invalid_cause)
            return verification
