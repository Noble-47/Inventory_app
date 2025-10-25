import uuid

from pydantic import model_serializer
from sqlmodel import SQLModel, Field


class ShopView(SQLModel, table=True):
    __tablename__ = "shop_view"

    id: int | None = Field(default=None, primary_key=True)
    business_id: uuid.UUID = Field(index=True)
    shop_id: uuid.UUID = Field(unique=True)
    location: str
    manager: str | None
    manager_email: str | None

    @model_serializer
    def serialize(self):
        return {
            "id": self.shop_id,
            "business_id": self.business_id,
            "location": self.location,
            "manager": self.manager,
            "manager_email": self.manager_email,
        }


class BusinessView(SQLModel, table=True):
    __tablename__ = "business_view"

    id: int | None = Field(default=None, primary_key=True)
    business_id: uuid.UUID
    name: str = Field(index=True)
    owner_name: str
    owner_id: int

    @model_serializer
    def serialize(self):
        return {"id": self.business_id, "name": self.name, "owner": self.owner_name}
