"""
For Exchange Service

# Exchange Service
Listens to: debt tracker channel
listens for: payment_made, debt_waived
"""

from sales.domain import commands
from sales.handlers import handle


def update_amount_paid(**kwargs):
    shop_id = kwargs["shop_id"]
    sale_ref = kwargs["sale_ref"]
    amount_paid = kwargs["amount_paid"]
    command = commands.UpdateSale(
        shop_id=shop_id, ref=sale_ref, updates={"amount_paid": amount_paid}
    )
    handle(command)


def effect_debt_waived(**kwargs):
    shop_id = kwargs["shop_id"]
    ref = kwargs["sale_ref"]
    command = commands.WaiveDebt(shop_id=shop_id, ref=ref)
    handle(command)


def create_record(**kwargs):
    shop_id = kwargs["shop_id"]
    command = commands.CreateShopRecord(shop_id=shop_id)


def delete_record(**kwargs):
    shop_id = kwargs["shop_id"]
    command = commands.DeleteShopRecord(shop_id=shop_id)


def initialize_hub(hub):
    exchange = hub.create_exchange("sales")

    exchange.establish_channel(
        channel="sales_notifications", subjects=["new_sale", "sale_update"]
    )

    exchange.listen_on(subject="new_shop_added", handler=create_record)

    exchange.listen_on(subject="shop_removed", handler=delete_record)

    # exchange.listen_on(
    #    subject="inventory_setting_update", handler=update_inventory_setting
    # )

    # exchange.listen_on(
    #    subject = "payment_made",
    #    handler = update_amount_paid
    # )

    # exchange.listen_on(
    #    subject ="debt_waived",
    #    handler = effect_debt_waived
    # )
