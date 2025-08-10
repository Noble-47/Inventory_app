from uuid import UUID

from shared import get_rotating_logger
from stock_port.domain import commands
from stock_port.domain import events
from exchange.hub import publish
from stock_port import exceptions
from stock_port.db import DB

from stock_port.domain.models import batch_ref_gen, BatchLine

logger = get_rotating_logger("orders", "orders.log")


def create_record(cmd: commands.CreateShopRecord, db):
    with db:
        db.records.create(cmd.shop_id)
        db.commit()


def delete_record(cmd: commands.DeleteShopRecord, db):
    with db:
        db.records.delete(cmd.shop_id)
        db.commit()


def create_order(cmd: commands.CreateOrder, db):
    with db:
        supplier = db.suppliers.get(
            shop_id=cmd.shop_id,
            firstname=cmd.firstname,
            lastname=cmd.lastname,
            phone=str(cmd.phone),
        )
        batchline = [
            BatchLine(
                batch_ref=batch_ref_gen(b.sku, b.quantity),
                sku=b.sku,
                cost=b.cost,
                expected_quantity=b.quantity,
            )
            for b in cmd.orderline
        ]
        order = db.orders.create(
            supplier=supplier,
            shop_id=cmd.shop_id,
            expected_delivery_date=cmd.delivery_date,
            cost=sum(b.cost for b in batchline),
            batchline=batchline,
        )
        db.commit()


def delete_order(cmd: commands.DeleteOrder, db):
    with db:
        db.orders.delete(shop_id=cmd.shop_id, order_id=cmd.order_id)
        db.commit()


def cancel_order(cmd: commands.CancelOrder, db):
    with db:
        order = db.orders.get(shop_id=cmd.shop_id, order_id=cmd.order_id)
        if order is None:
            raise exceptions.OrderNotFound()
        order.cancel(reason=cmd.reason)
        db.commit()


def process_delivery(cmd: commands.ProcessDelivery, db):
    with db:
        order = db.orders.get(shop_id=cmd.shop_id, order_id=cmd.order_id)
        order.process_delivery(orderline=cmd.orderline)
        db.commit()


def publish_order_delivered(event: events.OrderCompleted, db):
    logger.info("[x] Publishing order delivered")
    publish("delivery_notifications", "new_deliveries", event.json())


def publish_new_order(event: events.OrderCreated, db):
    logger.info("[x] Publishing new order created")
    publish("delivery_notifications", "new_order", event.json())


def publish_order_updated(event: events.OrderUpdated, db):
    logger.info("[x] Publishing order updated")
    publish("delivery_notifications", "order_updated", event.json())


def publish_order_cancelled(event: events.OrderCancelled, db):
    logger.info("[x] Publishing order cancelled")
    publish("delivery_notifications", "order_cancelled", event.json())


def log_event(event: events.Event, db):
    with db:
        db.audit.add(event)
        db.commit()


command_handlers = {
    commands.DeleteOrder: [delete_order],
    commands.CreateOrder: [create_order],
    commands.CancelOrder: [cancel_order],
    commands.ProcessDelivery: [process_delivery],
    commands.DeleteShopRecord: [delete_record],
    commands.CreateShopRecord: [create_record],
}


event_handlers = {
    events.OrderCreated: [publish_new_order, log_event],
    events.OrderCompleted: [publish_order_delivered, log_event],
    events.OrderUpdated: [publish_order_updated, log_event],
}


def handle(command):
    db = DB()
    logger.info(f"Received command {command}")
    for handler in command_handlers.get(type(command)):
        logger.info(f"Handling command with {handler.__name__}")
        try:
            handler(command, db)
        except Exception as e:
            logger.error(f"Error {handler.__name__} : {e}")
            raise e
        else:
            logger.info("done")
    # add event listners here if necessary
    for event in db.collect_events():
        logger.info(f"Received event {event}")
        for handler in event_handlers.get(type(event), []):
            logger.info(f"Handling event with {handler.__name__}")
            try:
                handler(event, db)
            except Exception as e:
                logger.error(f"Error {handler.__name__} : {e}")
            else:
                logger.info("Done")
