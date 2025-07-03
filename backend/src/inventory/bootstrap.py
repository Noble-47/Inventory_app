from functools import partial

from inventory.orm import start_mappers
from inventory.service import handlers
from inventory.domain import commands
from inventory.domain import events

from inventory.service.uow import UnitOfWork
from inventory.service.messagebus import MessageBus


def bootstrap(start_mapper=True):
    if start_mapper:
        start_mappers()

    uow = UnitOfWork()
    command_handlers = inject_command_handlers(uow)
    event_handlers = inject_event_handlers(uow)
    bus = MessageBus(command_handlers, event_handlers, uow)
    return bus


def inject_command_handlers(uow):
    return {
        commands.CreateStock: [partial(handlers.create_stock, uow=uow)],
        commands.AddBatchToStock: [partial(handlers.add_batch_to_stock, uow=uow)],
        commands.DispatchGoodsFromStock: [
            partial(handlers.dispatch_goods_from_stock, uow=uow)
        ],
        commands.UpdateBatchQuantity: [
            partial(handlers.update_batch_quantity, uow=uow)
        ],
        commands.UpdateBatchPrice: [partial(handlers.update_batch_price, uow=uow)],
    }


def inject_event_handlers(uow):
    return {
        events.BatchAddedToStock: [handlers.reflect_batch_add_in_view, log_batch_event],
        events.DispatchFromStock: [
            handlers.reflect_stock_dispatch_in_view,
            handlers.log_stock_event,
        ],
        events.DispatchFromBatch: [
            handlers.reflect_batch_dispatch_in_view,
            handlers.log_batch_event,
        ],
        events.UpdatedBatchPrice: [
            handlers.update_batch_view_price,
            handlers.log_batch_event,
        ],
        events.IncreasedStockLevel: [
            handlers.raise_stock_view_level,
            handlers.log_stock_event,
        ],
        events.DecreasedStockLevel: [
            handlers.lower_stock_view_level,
            handlers.log_stock_event,
        ],
        events.BatchSoldOut: [handlers.log_batch_event],
        events.StockSoldOut: [handlers.log_stock_event],
    }
