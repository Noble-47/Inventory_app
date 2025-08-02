from datetime import datetime
from shared import TIMEZONE

from stock_port.domain import commands
from stock_port.handlers import handle
from shared import get_rotating_logger


logger = get_rotating_logger("exchange-orders", "exchange.log")

def create_record(**kwargs):
    logger.info(" [ORD] Creating new inventory")
    command = commands.CreateShopRecord(shop_id=kwargs["shop_id"])
    handle(command)


def delete_record(**kwargs):
    shop_id = kwargs["shop_id"]
    logger.info("     [ORD] Removing inventory record")
    command = commands.DeleteShopRecord(shop_id=shop_id)
    handle(command)


def initialize_hub(hub):
    logger.info("[x] Initializing orders service...")
    exchange = hub.create_exchange("orders")
    exchange.establish_channel(
        channel="tracker_notifications",
        subjects=["new_order", "new_deliveries", "order_cancelled", "order_updated"],
    )

    exchange.listen_on(subject="new_shop_added", handler=create_record)
    exchange.listen_on(subject="shop_removed", handler=delete_record)
    logger.info("Done.")
