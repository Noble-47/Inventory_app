from sqlmodel import select

from stock_port.domain.models import Record
from stock_port.db import db_session


def get_report(shop_id):
    session = next(db.db_session())
    record = session.exec(select(Record).where(Record.shop_id == shop_id)).first()
    report = {"count": record.count, "value": record.value}
    session.close()
    return report
