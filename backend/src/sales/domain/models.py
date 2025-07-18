from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship

from shared import datetime_now_func

class Customer(SQLModel, table=True):
    __tablename__ = "customers"
    phone:str = Field(primary_key=True)
    title:str  = Field(default=None)
    firstname:str
    lastname:str = Field(default=None)

    @property
    def fullname(self):
        return (f"{self.title} " or "") + self.firstname + (f" {self.lastname}" or "")

class Product(SQLModel, table=True):
    __tablename__ = "products"
    sku:str = Field(primary_key=True)
    name:str

class SaleProductLink(SQLModel, table=True):
    sale_ref : UUID = Field(default=None, foreign_key= "sales.ref", primary_key=True)
    product_sku : str = Field(foreign_key = "products.sku", primary_key=True)
    quantity : int
    price_at_sale : float


class Sale(SQLModel, table=True):
    __tablename__ = "sales"
    shop_id:UUID
    ref: UUID = Field(default_factory=uuid4, primary_key=True)
    customer_phone:str|None = Field(default=None, foreign_key="customers.phone")
    customer: Customer = Relationship()
    amount_paid:float
    selling_price:float
    products:list[SaleProductLink] = Relationship()
    date:datetime = Field(default_factory=datetime_now_func)

    @property
    def cost_price(self):
        return sum(product.price for product in self.products)

    @property
    def markup(self):
        return self.cost_price == self.selling_price

class SaleAudit(SQLModel, table=True):
    __tablename__ = "sales_audit"
    id : int |  None = Field(default=None, primary_key=True)
    shop_id:UUID
    ref:UUID
    description:str
    time:float
    event_hash:str = Field(unique=True)
    payload:str

