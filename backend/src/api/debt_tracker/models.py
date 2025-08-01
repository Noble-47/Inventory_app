from datetime import datetime

from pydantic import BaseModel, Field


class Debt(BaseModel):
    sale_ref: str
    amount_paid: float
    selling_price: float
    last_paid_date: datetime | None = Field(default=None)


class Debtor(BaseModel):
    firstname: str
    lastname: str
    phone: str
    debts: list[Debt]


class DebtRead(Debt):
    firstname: str
    lastname: str
    phone: str


class DebtWrite(BaseModel):
    firstname: str
    lastname: str
    phone: str
    amount_paid: float
    selling_price: float


class DebtorList(BaseModel):
    shop_id: str
    debtors: list[Debtor]


class Log(BaseModel):
    audit_id: int
    sale_ref: str
    firstname: str
    lastname: str
    phone: str
    description: str
    time: datetime
    payload: str


class DebtLog(BaseModel):
    shop_id: str
    logs: list[Log]


class Payment(BaseModel):
    sale_ref: str
    amount: float


# Query Models
class DebtQueryParams(BaseModel):
    customer_name: str | None = ""
    customer_phone: str | None = ""
    min_amount_owed: float | None = Field(default=None)
    max_amount_owed: float | None = Field(default=None)
    start_date: datetime | None = Field(default=None)
    end_date: datetime | None = Field(default=None)
