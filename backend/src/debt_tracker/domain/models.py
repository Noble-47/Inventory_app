from typing import Optional, ClassVar
from datetime import datetime

from sqlalchemy.orm import registry
from sqlmodel import SQLModel, Field, Relationship

from debt_tracker.domain import events
from shared import datetime_now_func


def manual_ref_generator():
    return f"ENTRY-{datetime_now_func().strftime('%d-%m-%y-%H-%M-%S')}"


class BaseModel(SQLModel, registry=registry()):
    pass


class Debtor(BaseModel, table=True):
    __tablename__ = "debtors"
    firstname: str
    lastname: str
    phone: str = Field(primary_key=True)
    debts: list["Debt"] = Relationship()

    @property
    def active(self):
        return bool(next((debt.cleared == False for debt in self.debts), False))


class Debt(BaseModel, table=True):
    shop_id: str = Field(foreign_key="records.shop_id")
    debtor_phone: str = Field(foreign_key="debtors.phone")
    sale_ref: str = Field(primary_key=True)
    amount_paid: float
    selling_price: float
    cleared: bool = Field(default=False)
    date: datetime = Field(default_factory=datetime_now_func)
    last_paid_date: Optional[datetime] = Field(default=None)
    active_record_id: int | None = Field(default=None, foreign_key="active_records.id")
    active_record: Optional["ActiveRecord"] = Relationship()

    debtor: Optional[Debtor] = Relationship(back_populates="debts")
    events: ClassVar[list] = []

    @property
    def balance(self):
        return self.selling_price - self.amount_paid

    def __hash__(self):
        return hash(self.sale_ref)

    def increment_amount_paid(self, amount):
        self.amount_paid += amount
        self.events.append(
            events.PaymentReceived(
                shop_id=self.shop_id,
                phone=self.debtor.phone,
                firstname=self.debtor.firstname,
                lastname=self.debtor.lastname,
                sale_ref=self.sale_ref,
                amount_paid=amount,
            )
        )
        self.last_paid_date = datetime_now_func()
        if self.balance == 0:
            self.cleared = True
            self.events.append(
                self.DebtCleared(
                    shop_id=self.shop_id,
                    phone=self.debtor.phone,
                    firstname=self.debtor.firstname,
                    lastname=self.debtor.lastname,
                    sale_ref=self.sale_ref,
                    reason="Payment completed",
                )
            )
            self.active_record.to_deactivate()

    def waive(self):
        self.cleared = True
        self.events.append(
            events.DebtCleared(
                shop_id=self.shop_id,
                phone=self.debtor.phone,
                firstname=self.debtor.firstname,
                lastname=self.debtor.lastname,
                sale_ref=self.sale_ref,
                reason="Debt waived",
            )
        )
        self.active_record.to_deactivate()


class ActiveRecord(BaseModel, table=True):
    __tablename__ = "active_records"
    id: int | None = Field(default=None, primary_key=True)
    shop_id: str = Field(foreign_key="records.shop_id")
    debtor_phone: str = Field(foreign_key="debtors.phone")
    active_debts: list[Debt] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(Debt.active_record_id == ActiveRecord.id, Debt.debtor_phone == ActiveRecord.debtor_phone, Debt.cleared == False)"
        },
        back_populates="active_record",
    )
    active: bool = Field(default=True)

    def to_deactivate(self):
        self.active = any(debt for debt in self.active_debts)


class DebtLog(BaseModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    shop_id: str = Field(foreign_key="records.shop_id")
    sale_ref: str
    firstname: str
    lastname: str | None = Field(default=None)
    phone: str
    description: str
    time: datetime
    payload: str


class Record(BaseModel, table=True):
    __tablename__ = "records"
    shop_id: str = Field(primary_key=True)
    deleted: bool = Field(default=False)
    debts: list[Debt] = Relationship()

    @property
    def count(self):
        return len([debt for debt in self.debts if debt.cleared == False])

    @property
    def value(self):
        return sum(debt.balance for debt in self.debts if debt.cleared == False)
