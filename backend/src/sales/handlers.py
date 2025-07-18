from uuid import UUID

from sales.domain import commands
from sales.db import DB

from exchange.hub import publish


def create_sale(cmd:commands.CreateSale, db):
    with db:
        customer = db.customers.get_or_create(phone=cmd.phone_number, firstname=cmd.firstname, lastname=cmd.lastname)
        db.sales.add(shop_id=cmd.shop_id, products=cmd.products, selling_price=cmd.selling_price, customer=customer, amount_paid=cmd.amount_paid)
        db.commit()

def update_sale(cmd:commands.UpdateSale, db):
    customer_fields = ["firstname", "lastname", "phone_number"]
    products = []
    with db:
        if any((key in customer_fields) for key in cmd.updates.keys()):
            db.customers.update(
                phone = updates["phone_number"],
                firstname = updates.get("firstname"),
                lastname = updates.get("lastname")
            )

        if "products" in updates:
            products = updates.pop("products")

        for product_update in products:
            to_update = next((product for product in sale.products if product.sku == product_update["sku"]), None)
            if to_update is None:
                continue

            for kw, value in to_update:
                setattr(product, kw, value)

        db.sales.update(shop_id=cmd.shop_id, ref=cmd.sale_ref, updates=cmd.updates)
        db.commit()
        return

def delete_sale(cmd:commands.DeleteSale, db):
    with db:
        db.sales.delete(shop_id=cmd.shop_id, ref=cmd.sale_ref)
        db.commit()

handlers = {
    commands.DeleteSale : [delete_sale],
    commands.UpdateSale : [update_sale],
    commands.CreateSale : [create_sale]
}

def handle(command):
    db = DB()
    for handler in command_handlers.get(command):
        handler(command, db)
    # add event listners here if necessary
