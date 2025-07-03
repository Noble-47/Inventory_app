from sqlmodel import Session
from sqlmodel import select

from shopify.domain import models
from shopify.utils import get_password_hash
from shopify.db import events
from shopify import db


class Account(db.BaseRepo):

    def _create(
        self,
        firstname: str,
        lastname: str,
        email: str,
        password: str,
        account_type: str | None = None,
    ):
        password_hash = get_password_hash(password)
        account = models.Account(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password_hash=password_hash,
            account_type=account_type,
        )
        self.session.add(account)
        self.events.append(
            events.NewAccountCreated(
                email=email, firstname=firstname, lastname=lastname
            )
        )
        return account

    def _get(self, email: str):
        account = self.session.exec(
            select(models.Account).where(models.Account.email == email)
        ).first()
        return account

    def check_email_exists(self, email: str):
        return (
            self.session.exec(
                select(models.Account.id).where(models.Account.email == email)
            ).first()
            is not None
        )
