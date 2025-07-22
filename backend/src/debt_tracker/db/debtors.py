from sqlmodel import select

from debt_tracker.domain.models import Debtor
from debt_tracker.domain import messages


class DebtorDB:

    def __init__(self, session, events):
        self.session = session
        self.events = events

    def get(
        self, shop_id: str, phone: str, firstname: str, lastname: str, trigger=True
    ):
        debtor = self.session.exec(select(Debtor).where(Debtor.phone == phone)).first()
        if debtor is None:
            return
        if trigger and ((debtor.firstname, debtor.lastname) != (firstname, lastname)):
            self.events.append(
                messages.InfoMismatch(
                    shop_id=shop_id,
                    phone=phone,
                    recorded_firstname=debtor.firstname,
                    recorded_lastname=debtor.lastname,
                    input_firstname=firstname,
                    input_lastname=lastname,
                )
            )
        return debtor

    def add(
        self, shop_id: str, phone: str, firstname: str, lastname: str | None = None
    ):
        debtor = self.get(shop_id, phone, firstname, lastname)
        if debtor is None:
            debtor = Debtor(phone=phone, firstname=firstname, lastname=lastname)
            self.session.add(debtor)
        return debtor
