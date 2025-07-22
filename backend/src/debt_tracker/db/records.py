from sqlmodel import select

from debt_tracker.domain.models import Record, Debt, Debtor, DebtLog, ActiveRecord


class RecordsDB:

    def __init__(self, session, event=None):
        self.session = session

    def create(self, shop_id):
        if self.get(shop_id):
            return
        record = Record(shop_id=shop_id)
        self.session.add(record)

    def get_active_record(self, shop_id, debtor_phone):
        active_record = self.session.exec(
            select(ActiveRecord).where(
                ActiveRecord.shop_id == shop_id,
                ActiveRecord.debtor_phone == debtor_phone,
            )
        ).first()
        if active_record is None:
            active_record = ActiveRecord(shop_id=shop_id, debtor_phone=debtor_phone)
        self.session.add(active_record)
        return active_record

    def record_debt(self, shop_id, debt):
        active_record = self.get_active_record(shop_id, debt.debtor.phone)
        active_record.active_debts.append(debt)

    def delete(self, shop_id):
        record = self.get(shop_id)
        if record is None:
            return
        record.deleted = True

    def get(self, shop_id):
        return self.session.exec(
            select(Record).where(Record.shop_id == shop_id, Record.deleted == False)
        ).first()

    def is_deleted(self, shop_id):
        return bool(self.get(shop_id))

    def fetch_debts(self, shop_id, query):
        stmt = select(Debt).join(Debtor, isouter=True)

        if query.firstname:
            stmt = stmt.where(Debtor.firstname.ilike(query.firstname))
        if query.lastname:
            stmt = stmt.where(Debtor.lastname.ilike(query.lastname))
        if query.phone_number:
            stmt = stmt.where(Debtor.phone == query.phone_number)
        if query.start_date:
            stmt = stmt.where(Debt.date >= query.start_date)
        if query.end_date:
            stmt = stmt.where(Debt.date <= query.end_date)

        results = self.session.exec(stmt).all()
        return results

    def get_debt_detail(self, shop_id, sale_ref):
        if self.is_deleted(shop_id):
            return

        debt = self.session.exec(
            select(Debt).where(Debt.sale_ref == sale_ref, Debt.shop_id == shop_id)
        ).first()
        return debt

    def get_debt_log(self, shop_id):
        if self.is_deleted(shop_id):
            return

        return self.session.exec(
            select(DebtLog).where(DebtLog.shop_id == shop_id)
        ).all()

    def get_debtors(self, shop_id):
        if self.is_deleted(shop_id):
            return

        return self.session.exec(
            select(Debtor)
            .join(ActiveRecord)
            .where(ActiveRecord.shop_id == shop_id, ActiveRecord.active == False)
        ).all()
