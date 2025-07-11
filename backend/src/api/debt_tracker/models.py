from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Debt(BaseModel):
    purchase_ref: str
    amount_paid: float
    amound_owed: float
    last_paid: float
    last_paid_date: datetime
    date: datetime
    paid: bool


class Debtor(BaseModel):
    name: str
    phone_number: str
    debts: list[Debt]


class DebtModel(Debt):
    name: str
    phone_number: str


class DebtorList(BaseModel):
    shop_id: UUID
    debtors: list[Debtor]


# Query Models
class DebtQueryParams(BaseModel):
    purchase_ref: str | None = ""
    customer_name: str | None = ""
    customer_phone: str | None = ""
    product: str | None = ""
    min_amount_owed: float | None = Field(default=None)
    max_amount_owed: float | None = Field(default=None)
    start_date: datetime | None = Field(default=None)
    end_date: datetime | None = Field(default=None)
