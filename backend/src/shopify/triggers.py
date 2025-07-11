from shopify.config import get_default_notifier
from shopify import db


def send_invite_email(session, token):
    business_name = db.Business(session).get_business_name(token.business_id)
    notifier = get_default_notifier()
    notifier.send_invite_email(
        business_name=business_name, email=token.email, token=token.token_str
    )
    token.sent = True
    session.commit()
