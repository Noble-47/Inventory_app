import uuid

from sqlmodel import SQLModel, Field


class ShopView(SQLModel, table=True):
    __tablename__ = "shop_view"

    id : int | None = Field(default=None, primary_key=True)
    business_id: uuid.UUID = Field(index=True)
    shop_id: uuid.UUID
    location: str
    manager: str
    manager_id: str

class BusinessView(SQLModel, table=True):
    __tablename__ = "business_view"

    id : int | None = Field(default=None, primary_key=True)
    business_id: uuid.UUID
    name: str = Field(index=True)
    owner_name: str
    owner_id: int
