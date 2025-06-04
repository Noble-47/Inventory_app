from functools import partial

from shopify.db import events as db_events
from shopify.service import handlers
from shopify.domain import events
from shopify import config
from shopify import db

from shopify.service.uow import UnitOfWork
from shopify.service.messagebus import MessageBus
from shopify.notification.email import ConsoleEmailNotifier


def bootstrap(email_notifier=ConsoleEmailNotifier()):
    uow = UnitOfWork()
    command_handlers = inject_command_handlers(uow)
    event_handlers = inject_event_handlers(uow, email_notifier)
    bus = MessageBus(command_handlers, event_handlers, uow)
    return bus


def inject_command_handlers(uow):
    return dict(
        (command, [partial(handler, uow=uow) for handler in handlers])
        for command, handlers in handlers.COMMAND_HANDLERS.items()
    )


def inject_event_handlers(uow, notifier):
    return {
        events.NewBusinessCreated: [
            partial(handlers.log_audit, uow=uow),
            partial(handlers.add_business_to_views, uow=uow),
            partial(handlers.setup_new_business, uow=uow)
        ],
        events.AddedNewShop: [
            partial(handlers.log_audit, uow=uow),
            partial(handlers.add_shop_to_views, uow=uow),
        ],
        events.RemovedShop: [
            partial(handlers.log_audit, uow=uow),
            partial(handlers.remove_shop_from_views, uow=uow),
        ],
        events.AssignedNewManager: [partial(handlers.log_audit, uow=uow)],
        events.DismissedManager: [partial(handlers.log_audit, uow=uow)],
        events.CreatedManagerInviteToken: [partial(handlers.log_audit, uow=uow)],
        db_events.NewAccountCreated: [
            partial(
                handlers.create_and_send_verification_token, notifier=notifier, uow=uow
            )
        ],
    }
