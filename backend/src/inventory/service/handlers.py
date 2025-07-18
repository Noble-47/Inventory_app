from inventory.domain import events, commands
from inventory import exceptions

from inventory.service.uow import UnitOfWork
from inventory.domain.models import sku_generator
from inventory.settings import SQLSettingPersistor, apply_default_settings


# command handlers
def create_stock(command: commands.CreateStock, uow: UnitOfWork):
    with uow:
        sku = sku_generator(name=command.name)
        if uow.stocks.check_exists(sku, command.shop_id):
            raise exceptions.DuplicateStockRecord(
                f"Duplicate record of {command.name} with sku {sku}"
            )
        stock = uow.stocks.create(
            sku=sku,
            name=command.name,
            shop_id=command.shop_id,
            quantity=command.quantity,
            price=command.price,
        )
        uow.commit()


def delete_stock(command: commands.DeleteStock, uow: UnitOfWork):
    with uow:
        uow.stocks.delete(shop_id=command.shop_id, sku=command.sku)
        uow.commit()


def add_batch_to_stock(command: commands.AddBatchToStock, uow: UnitOfWork):
    with uow:
        stock = uow.stocks.get(sku=command.sku, shop_id=command.shop_id)
        stock.add(
            ref=command.batch_ref,
            quantity=command.quantity,
            price=command.price,
            timestamp=command.timestamp,
        )
        uow.commit()


def dispatch_goods_from_stock(command: commands.DispatchGoods, uow: UnitOfWork):
    with uow:
        stock = uow.stocks.get_only_dispatchable_batches(
            sku=command.sku, shop_id=command.shop_id
        )
        stock.dispatch(quantity=command.quantity, timestamp=command.timestamp)
        uow.commit()


def update_batch_quantity(command: commands.UpdateBatchQuantity, uow: UnitOfWork):
    with uow:
        stock = uow.stocks.get(sku=command.sku, shop_id=command.shop_id)
        stock.update_batch_quantity(
            batch_ref=command.batch_ref, quantity=command.quantity
        )
        uow.commit()


def update_batch_price(command: commands.UpdateBatchPrice, uow: UnitOfWork):
    with uow:
        stock = uow.stocks.get(sku=command.sku, shop_id=command.shop_id)
        stock.update_batch_price(command.batch_ref, command.price)
        uow.commit()


def update_stock_quantity(command: commands.UpdateStockQuantity):
    with uow:
        stock = uow.stocks.get(sku=command.sku, shop_id=command.shop_id)
        stock.update_quantity(
            command.quantity, incremental=command.incremental, price=command.price
        )


def update_setting(command: commands.UpdateSetting):
    setting_persistor = SQLSettingPersistor()
    setting_persistor.update(
        shop_id=command.shop_id, name=command.name, value=command.value
    )


def create_inventory(command: commands.CreateInventory, uow: UnitOfWork):
    with uow:
        uow.inventory.add(command.shop_id)
        uow.commit()
        apply_default_settings(shop_id)


def delete_inventory(command: commands.DeleteInventory, uow: UnitOfWork):
    with uow:
        uow.inventory.remove(command.shop_id)
        uow.commit()


# Event handlers


def log_stock_event(event: events.Event, uow: UnitOfWork):
    with uow:
        uow.stock_audit.add(event)
        uow.commit()


def log_batch_event(event: events.Event, uow: UnitOfWork):
    with uow:
        uow.batch_audit.add(event)
        uow.commit()
