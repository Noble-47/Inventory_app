from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import registry

from shared import datetime_now_func


class SalesModel(SQLModel, registry=registry()):
    pass


class Customer(SalesModel, table=True):
    __tablename__ = "customers"
    phone: str = Field(primary_key=True)
    title: str | None = Field(default=None)
    firstname: str
    lastname: str

    @property
    def fullname(self):
        return f"{self.title or ''}" + self.firstname + f"{self.lastname or ''}"

    def __hash__(self):
        return hash(self.phone)


class Product(SalesModel, table=True):
    __tablename__ = "products"
    sku: str = Field(primary_key=True)
    name: str


class SaleProductLink(SalesModel, table=True):
    sale_ref: UUID = Field(default=None, foreign_key="sales.ref", primary_key=True)
    product_sku: str = Field(foreign_key="products.sku", primary_key=True)
    quantity: int
    price_at_sale: float


class Sale(SalesModel, table=True):
    __tablename__ = "sales"
    shop_id: UUID = Field(foreign_key="records.shop_id")
    ref: UUID = Field(default_factory=uuid4, primary_key=True)
    customer_phone: str | None = Field(default=None, foreign_key="customers.phone")
    customer: Customer = Relationship()
    amount_paid: float
    selling_price: float
    products: list[SaleProductLink] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
    date: datetime = Field(default_factory=datetime_now_func)

    def serialize(self):
        return {
            "ref": self.ref,
            "customer_phone": self.customer_phone,
            "customer": self.customer.fullname,
            "amount_paid": self.amount_paid,
            "selling_price": self.selling_price,
            "date": self.date.timestamp(),
            "products": {
                "sku": product.product_sku,
                "quantity": product.quantity,
                "price_at_sale": product.price_at_sale,
            },
        }

    @property
    def cost_price(self):
        return sum(product.price_at_sale for product in self.products)

    @property
    def markup(self):
        return self.cost_price == self.selling_price

    def update(
        self,
        customer=None,
        firstname=None,
        lastname=None,
        products=None,
        selling_price=None,
        amount_paid=None,
    ):
        if customer:
            self.customer = customer
        self.selling_price = selling_price or self.selling_price
        self.amount_paid = amount_paid or self.amount_paid
        product_updates = products or []
        for update in product_updates:
            product = next(
                (product for product in self.products if product.sku == update["sku"]),
                None,
            )
            if product is None:
                product = SaleProductLink(**update)
                self.products.append(product)
            else:
                for kw, value in update.items():
                    setattr(product, kw, value)


class Record(SalesModel, table=True):
    __tablename__ = "records"
    shop_id: UUID = Field(primary_key=True)
    deleted: bool = Field(default=False)
    sales: list[Sale] = Relationship()

    @property
    def count(self):
        return len(self.sales)

    @property
    def value(self):
        return sum(sale.selling_price for sale in self.sales)


class SaleAudit(SalesModel, table=True):
    __tablename__ = "sales_audit"
    id: int | None = Field(default=None, primary_key=True)
    shop_id: UUID
    ref: UUID = Field(nullable=True)
    description: str
    time: float
    event_hash: str = Field(unique=True)
    payload: str
