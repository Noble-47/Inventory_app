from inventory import exceptions
from inventory.domain import events, commands

from inventory.domain.models import sku_generator
from inventory.service.uow import UnitOfWork

# command handlers
def create_stock(command:commands.CreateStock, uow:UnitOfWork):
    with uow:
        sku = sku_generator(command.stock_name, command.shop_id)
        if uow.stocks.check_exists(sku):
            raise exceptions.DuplicateStock(f"Duplicate record of {command.stock_name} with global sku {sku}")
        stock = uow.stocks.create(sku=sku, name=command.stock_name, shop_id=command.shop_id, quantity=cmd.quantity)

def add_batch_to_stock(command:commands.AddBatchToStock, uow:UnitOfWork):
    with uow:
        stock = uow.stocks.get(command.sku)
        stock.add(ref=command.batch_ref, quantity=command.quantity, price=command.price, timestamp=command.timestamp)
        uow.commit()

def dispatch_goods_from_stock(command:commands.DispatchGoodsFromStock, uow:UnitOfWork):
    with uow:
        stock = uow.stocks.get_only_dispatchable_batches(command.sku)
        stock.dispatch(quantity=command.quantity, timestamp=command.timestamp)
        uow.commit()

def update_batch_quantity(command:commands.UpdateBatchQuantity, uow:UnitOfWork):
    with uow:
        stock = uow.stocks.get(command.sku)
        stock.update_batch_quantity(batch_ref=command.batch_ref, quantity=command.quantity)
        uow.commit()

def update_batch_price(command:commands.UpdateBatchPrice, uow:UnitOfWork):
    with uow:
        stock = uow.stocks.get(command.sku)
        stock.update_batch_price(command.batch_ref, command.price)
        uow.commit()

# Event handlers

def log_stock_event(event:events.Event, uow:UnitOfWork):
    with uow:
        uow.stock_audit.add(event)
        uow.commit()


def log_batch_event(event:events.Event, uow:UnitOfWork):
    with uow:
        uow.batch_audit.add(event)
        uow.commit()


def reflect_batch_add_in_view(event:events.BatchAddedToStock, uow:UnitOfWork):
    with uow:
        uow.views.update_stock_level(sku=event.sku, by=event.quantity)
        uow.views.add_batch(sku=event.sku, ref=event.batch_ref, price=event.price, stock_in_units=event.quantity, stock_time=event.datetime)
        uow.commit()


def reflect_stock_dispatch_in_view(event:events.DispatchedFromStock, uow:UnitOfWork):
    with uow:
        uow.views.update_stock_level(sku=event.sku, by=event.quantity, dispatch_time=event.dispatch_time)
        uow.commit()

def reflect_batch_dispatch_in_view(event:events.DispatchedFromBatch, uow:UnitOfWork):
        uow.views.update_batch_quantity(sku=event.sku, batch_ref=event.batch_ref, quantity=event.quantity)
        uow.commit()


def update_batch_view_price(event: events.UpdatedBatchPrice, uow:UnitOfWork):
    with uow:
        uow.views.update_batch_price(sku=event.sku, batch_ref=event.batch_ref, price=event.price)
        uow.commit()


def raise_stock_view_level(event:events.IncreasedStockLevel, uow:UnitOfWork):
    with uow:
       uow.views.update_stock_level(sku=event.sku, by=event.by, action="increase")
       for batch_ref, quantity in event.batch_adjustment_record:
           uow.views.update_batch_quantity(batch_ref, quantity)
        uow.commit()


def lower_stock_view_level(event:events.DecreasedStockLevel, uow:UnitOfWork):
    with uow:
       uow.views.update_stock_level(sku=event.sku, by=event.by, action="decrease")
       for batch_ref, quantity in event.batch_adjustment_record:
           uow.views.update_batch_quantity(batch_ref, quantity)
        uow.commit()
