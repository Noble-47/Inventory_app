from pydantic import BaseModel


class Command(BaseModel):
    pass


class CreateOrder(BaseModel):
    pass


class CancelOrder(BaseModel):
    pass


class MarkOrderAsDelivered(BaseModel):
    pass
