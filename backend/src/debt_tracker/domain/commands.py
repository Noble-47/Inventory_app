from pydantic import BaseModel, Field


class Command(BaseModel):
    pass


class RecordPayment(Command):
    sale_ref: str
    shop_id:str
    amount: float


class WaiveDebt(Command):
    shop_id: str
    sale_ref: str


class DeleteRecord(Command):
    shop_id: str


class CreateRecord(Command):
    shop_id: str


class RecordDebt(Command):
    shop_id: str
    phone: str
    firstname: str
    lastname: str
    amount_paid: float
    selling_price: float
    sale_ref:str | None = Field(default=None)


class UpdateDebtorInfo(Command):
    shop_id: str
    phone: str
    firstname: str | None = Field(default=None)
    lastname: str | None = Field(default=None)


class UpdateDebtInfo(Command):
    shop_id: str
    sale_ref: str
    selling_price: str | None = Field(default=None)
    amount_paid: str | None = Field(default=None)
