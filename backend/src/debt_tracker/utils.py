from sqlmodel import select

from debt_tracker.domain.models import Debt
from debt_tracker.db import db_session


def debt_exists(shop_id, sale_ref):
    session = next(db_session())
    stmt = select(Debt).where(Debt.shop_id == shop_id, Debt.sale_ref == sale_ref)
    result = session.exec(stmt).first() is not None
    session.close()
    return result
