from debt_tracker.db import DB
from debt_tracker.domain.models import Debt, Debtor, DebtLog


def get_debtors(shop_id):
    with DB() as db:
        debtors = db.records.get_debtors(shop_id)
        view = {"shop_id": shop_id}
        view["debtors"] = [
            {
                "firstname": debtor.firstname,
                "lastname": debtor.lastname,
                "phone": debtor.phone,
                "debts": [debt.model_dump() for debt in debtor.debts],
            }
            for debtor in debtors
        ]
        return view


def get_debts(shop_id, query=None):
    with DB() as db:
        debts = db.records.fetch_debts(shop_id, query)
        return [
            {
                "firstname": debt.debtor.firstname,
                "lastname": debt.debtor.lastname,
                "phone": debt.debtor.phone,
                "sale_ref": debt.sale_ref,
                "amount_paid": debt.amount_paid,
                "selling_price": debt.selling_price,
                "last_paid_date": debt.last_paid_date,
            }
            for debt in debts
        ]


def get_debt(shop_id, sale_ref):
    with DB() as db:
        debt = db.records.get_debt_detail(shop_id=shop_id, sale_ref=sale_ref)
        return {
            "firstname": debt.debtor.firstname,
            "lastname": debt.debtor.lastname,
            "phone": debt.debtor.phone,
            "sale_ref": debt.sale_ref,
            "amount_paid": debt.amount_paid,
            "selling_price": debt.selling_price,
            "balance": debt.balance,
            "last_paid_date": debt.last_paid_date,
        }


def get_debt_log(shop_id):
    with DB() as db:
        debt_log = db.records.get_debt_log(shop_id)
        view = {"shop_id": shop_id}
        logs = []
        for log in debt_log:
            logs.append(
                {
                    "audit_id": log.id,
                    "sale_ref": log.sale_ref,
                    "firstname": log.firstname,
                    "lastname": log.lastname,
                    "phone": log.phone,
                    "description": log.description,
                    "time": log.time,
                    "payload": log.payload,
                }
            )
        view["logs"] = logs
        return view
