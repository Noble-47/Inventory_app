from sqlmodel import Session
from sqlmodel import select

from shopify.domain import models
from shopify.utils import get_password_hash
from shopify.domain import events
from shopify import db


class Account(db.BaseRepo):

    def _create(firstname: str, lastname: str, email: str, password: str):
        password_hash = get_password_hash(password)
        account = models.Account(firstname, lastname, email, password_hash)
        self.session.add(account)
        self.events.append(
            events.NewAccountCreated(
                account.id, account.email, account.firstname, account.lastname
            )
        )
        return account

    def _get(email: str):
        account = self.session.exec(
            select(models.Account).where(models.Account.email == email)
        ).first()
        return account
