from sqlmodel import select

from sales.domain.models import Customer
from sales import exceptions

class CustomersDB:

    def __init__(self, session):
        self.session = session


    def add(self, phone:str, firstname:str, lastname:str):
        if self.check_exists(phone):
            # No two persons have the same phone number
            return self.get(phone)
        customer = Customer(phone=phone, firstname=firstname, lastname=lastname)
        self.session.add(customer)
        return customer

    def update(self, phone:str, firstname:str | None = None, lastname:str | None = None):
        if not self.check_exists(phone):
            return
        customer = self.get(phone, session)
        if firstname:
            customer.firstname = firstname
        if lastname:
            customer.lastname = lastname
        self.session.add(customer)
        return customer

    def check_exists(self, phone):
        stmt = select(Customer.phone).where(Customer.phone == phone)
        return bool(self.session.exec(stmt).first())

    def get(self, phone):
        stmt = select(Customer).where(Customer.phone == phone)
        customer = self.session.exec(stmt).first()
        return customer

    def get_or_create(self, phone, firstname, lastname):
        customer = self.get(phone)
        if customer is None:
            customer = self.add(phone, firstname, lastname)
        return customer
