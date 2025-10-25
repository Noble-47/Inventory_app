from sales.db import DB


def get_report(shop_id):
    with DB() as db:
        record = db.records.get(shop_id=shop_id)
        report = {"count": record.count, "value": record.value}
    return report
