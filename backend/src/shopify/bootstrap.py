from functools import partial

from shopify.service.messagebus import MessageBus
from shopify.service.uow import UnitOfWork
from shopify.service import handlers
from shopify import config
from shopify import db


def bootstrap(
    database_url=config.DATABASE_URL,
):
    db.create_tables(database_url)
    uow = UnitOfWork()
    command_handlers = inject_command_handlers(uow)
    event_handlers = inject_event_handlers(uow)
    bus = MessageBus(command_handlers, event_handlers, uow)
    return bus


def inject_command_handlers(uow):
    return [
        {command: [partial(handler, uow=uow) for handler in handlers]}
        for command, handlers in handlers.COMMAND_HANDLERS.items()
    ]


def inject_event_handlers(uow):
    return [
        {event: [partial(handler, uow=uow) for handler in handlers]}
        for event, handlers in handlers.EVENT_HANDLERS.items()
    ]
