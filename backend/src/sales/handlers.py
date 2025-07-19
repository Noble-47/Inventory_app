from uuid import UUID

from exchange.hub import publish
from sales.domain import events
from sales.domain import commands
from sales.db import DB


def create_record(cmd:commands.CreateShopRecord, db):
    with db:
        db.records.create(shop_id)
        db.commit()


def delete_record(cmd:commands.DeleteShopRecord, db):
    with db:
        db.records.delete(shop_id)
        db.commit()


def create_sale(cmd:commands.CreateSale, db):
    with db:
        customer = db.customers.get_or_create(phone=cmd.phone_number, firstname=cmd.firstname, lastname=cmd.lastname)
        for product in cmd.products:
            sku = product['product_sku']
            product['price_at_sale'] = cmd.inventory_record[sku].price
        db.sales.add(
            shop_id = cmd.shop_id,
            products = cmd.products,
            selling_price = cmd.selling_price,
            customer = customer,
            amount_paid = cmd.amount_paid
        )
        db.commit()

def update_sale(cmd:commands.UpdateSale, db):
    products = []
    with db:
        sale = db.sales.get(command.ref)
        updates = command.model_dump()
        updates.pop("ref")
        sale.update(**upadtes)
        db.commit()
        return

def delete_sale(cmd:commands.DeleteSale, db):
    with db:
        db.sales.delete(shop_id=cmd.shop_id, ref=cmd.sale_ref)
        db.commit()

def publish_new_sale(event:events.NewSaleAdded, db):
    print("[x] Publishing sale update")
    publish("sales_notifications", "new_sale", event.model_dump())

def publish_sale_update(event:events.SaleRecordUpdated, db):
    print("[x] Publishing sale update")
    publish("sales_notifications", "sale_update", event.model_dump())

def log_event(event:events.Event, db):
    with db:
        db.audit.add(event)
        db.commit()


command_handlers = {
    commands.DeleteSale : [delete_sale],
    commands.UpdateSale : [update_sale],
    commands.CreateSale : [create_sale],
    commands.DeleteShopRecord : [delete_record],
    commands.CreateShopRecord : [create_record]
}


event_handlers = {
    events.NewSaleAdded : [publish_new_sale, log_event],
    events.SaleRecordUpdated : [publish_sale_update, log_event]
}


def handle(command):
    db = DB()
    for handler in command_handlers.get(type(command)):
        handler(command, db)
    # add event listners here if necessary
    for event in db.collect_events():
        print(event)
        for handler in event_handlers.get(type(event), []):
            handler(event, db)
