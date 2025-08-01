from datetime import datetime
from shared import TIMEZONE

from stock_port.domain import commands
from stock_port.handlers import handle


def create_record(**kwargs):
    print(" [ORD] Creating new inventory")
    command = commands.CreateShopRecord(shop_id=kwargs["shop_id"])
    handle(command)


def delete_record(**kwargs):
    shop_id = kwargs["shop_id"]
    print("     [ORD] Removing inventory record")
    command = commands.DeleteShopRecord(shop_id=shop_id)
    handle(command)


def initialize_hub(hub):
    print("[x] Initializing orders service...", end="")
    exchange = hub.create_exchange("tracker")
    exchange.establish_channel(
        channel="tracker_notifications",
        subjects=["new_order", "new_deliveries", "order_cancelled", "order_updated"],
    )

    exchange.listen_on(subject="new_shop_added", handler=create_record)
    exchange.listen_on(subject="shop_removed", handler=delete_record)
    print("Done.")
