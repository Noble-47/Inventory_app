from debt_tracker.domain.models import Debt
from debt_tracker.domain import events
from sqlmodel import select


class DebtDB:

    def __init__(self, session, events):
        self.session = session
        self.events = events
        self.seen = set()

    def add(
        self,
        shop_id: str,
        sale_ref: str | str,
        phone: str,
        selling_price: float,
        amount_paid: float,
        debtor,
    ):
        debt = self.get(shop_id=shop_id, sale_ref=sale_ref)
        if debt:
            return debt
        debt = Debt(
            shop_id=shop_id,
            sale_ref=sale_ref,
            debtor_phone=phone,
            amount_paid=amount_paid,
            selling_price=selling_price,
        )
        self.session.add(debt)
        self.events.append(
            events.NewDebt(
                shop_id=shop_id,
                firstname=debtor.firstname,
                lastname=debtor.lastname,
                phone=debtor.phone,
                sale_ref=debt.sale_ref,
                selling_price=debt.selling_price,
                amount_paid=debt.amount_paid,
            )
        )
        debt.debtor = debtor
        self.seen.add(debt)
        return debt

    def get(self, shop_id: str, sale_ref: str):
        debt = self.session.exec(
            select(Debt).where(Debt.sale_ref == sale_ref, Debt.shop_id == shop_id)
        ).first()
        if debt:
            self.seen.add(debt)
        return debt
