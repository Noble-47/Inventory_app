from shopify.db import db_session
from shopify.db import events
from shopify import db


class VerificationNotifier:
    pass


class InventraNotifier:
    pass


def create_and_send_verification_token(
    events: events.NewAccountCreated, notifier: VerificationNotifier
):
    verification = db.AccountVerifier(session)
    token = verification.create(event.email)
    session.commit()
    notifier.send(token)


def notify_verification_success(
    events: events.AccountVerified, notifier: InventraNotifier
):
    # external notification system
    pass
