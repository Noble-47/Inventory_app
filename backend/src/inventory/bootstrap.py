from functools import partial

from inventory.service import handlers
from inventory.domain import commands
from inventory.domain import events

from inventory.service.uow import UnitOfWork
from inventory.adapters.orm import start_mappers
from inventory.service.message_bus import MessageBus


def bootstrap(start_mapper=True):
    if start_mapper:
        start_mappers()
    uow = UnitOfWork()
    command_handlers = inject_command_handlers(uow)
    event_handlers = inject_event_handlers(uow)
    bus = MessageBus(
        command_handlers=command_handlers, event_handlers=event_handlers, uow=uow
    )
    return bus


def inject_command_handlers(uow):
    return {
        commands.CreateStock: [partial(handlers.create_stock, uow=uow)],
        commands.AddBatchToStock: [partial(handlers.add_batch_to_stock, uow=uow)],
        commands.DispatchGoods: [partial(handlers.dispatch_goods_from_stock, uow=uow)],
        commands.UpdateBatchQuantity: [
            partial(handlers.update_batch_quantity, uow=uow)
        ],
        commands.UpdateBatchPrice: [partial(handlers.update_batch_price, uow=uow)],
        commands.CreateStock: [partial(handlers.create_stock, uow=uow)],
        commands.DeleteStock: [partial(handlers.delete_stock, uow=uow)],
    }


def inject_event_handlers(uow):
    return {
        events.BatchAddedToStock: [partial(handlers.log_batch_event, uow=uow)],
        events.DispatchedFromStock: [partial(handlers.log_stock_event, uow=uow)],
        events.DispatchedFromBatch: [partial(handlers.log_batch_event, uow=uow)],
        events.UpdatedBatchPrice: [partial(handlers.log_batch_event, uow=uow)],
        events.IncreasedStockLevel: [partial(handlers.log_stock_event, uow=uow)],
        events.DecreasedStockLevel: [partial(handlers.log_stock_event, uow=uow)],
        events.BatchSoldOut: [partial(handlers.log_batch_event, uow=uow)],
        events.StockSoldOut: [partial(handlers.log_stock_event, uow=uow)],
        events.StockCreated: [partial(handlers.log_stock_event, uow=uow)],
        events.StockDeleted: [partial(handlers.log_stock_event, uow=uow)],
    }
