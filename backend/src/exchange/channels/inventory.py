from datetime import datetime
from shared import TIMEZONE

from inventory.bootstrap import bootstrap
from inventory.domain import commands

try:
    bus = bootstrap(start_mapper=True)
except Exception as e:
    bus = bootstrap(start_mapper=False)


def create_inventory(**kwargs):
    print("[INV] Creating new inventory")
    command = commands.CreateInventory(shop_id=kwargs["shop_id"])
    bus.handle(command)


def remove_inventory(**kwargs):
    print("[INV] Removing inventory record")
    command = commands.DeleteInventory(shop_id=kwargs["shop_id"])
    bus.handle(command)


def update_inventory_setting(**kwargs):
    print("[INV] Removing inventory record")
    command = commands.UpdateSetting(
        shop_id=kwargs["shop_id"], name=kwargs["name"], value=kwargs["value"]
    )
    bus.handle(command)


def dispatch(**kwargs):
    print("[INV] Dispatching from inventory")
    products = kwargs["products"]
    timestamp = datetime.fromtimestamp(kwargs["date"], TIMEZONE)
    for stock in products:
        command = commands.DispatchGoods(
            shop_id=kwargs["shop_id"],
            sku=stock["sku"],
            quantity=stock["quantity"],
            timestamp=timestamp,
        )
        bus.handle(command)


def update_quantity(**kwargs):
    print("[INV] Updating product quantity")
    products = kwargs.get("products")
    if product is None:
        return
    command = commands.UpdateBatchQuantity(
        shop_id=kwargs["shop_id"],
        sku=kwargs["sku"],
        quantity=kwargs["quantity"],
        increment=kwargs["increment"],
        price=product["price"],
    )
    bus.handle(command)


def initialize_hub(hub):
    exchange = hub.create_exchange("inventory")

    exchange.listen_on(subject="new_shop_added", handler=create_inventory)

    exchange.listen_on(subject="shop_removed", handler=remove_inventory)

    exchange.listen_on(
        subject="inventory_setting_update", handler=update_inventory_setting
    )

    exchange.listen_on(subject="new_sale", handler=dispatch)

    exchange.listen_on(subject="sale_update", handler=update_quantity)
