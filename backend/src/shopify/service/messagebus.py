from collections import deque
from typing import Annotated
import logging

from shopify.domain import commands
from shopify.domain import events
from shopify import exceptions

from shopify.service.uow import UnitOfWork

Message = Annotated[events.Event, commands.Command]

logging.basicConfig(
    filename="newfile.log", format="[%(asctime)s] %(message)s", filemode="a"
)

logger = logging.getLogger()

logger.setLevel(logging.INFO)


class MessageBus:

    def __init__(
        self,
        command_handlers: dict[str, list[callable]],
        event_handlers: dict[str, list[callable]],
        uow: UnitOfWork,
    ):
        self.command_handlers = command_handlers
        self.event_handlers = event_handlers
        self.uow = uow

    def handle(self, message: Message):
        queue = deque()
        queue.append(message)
        while queue:
            message = queue.pop()
            if isinstance(message, events.Event):
                self.handle_event(message)
            elif isinstance(message, commands.Command):
                self.handle_command(message)
            queue.extend(self.uow.collect_events())

    def handle_event(self, event: events.Event):
        for handler in self.event_handlers.get(type(event), list()):
            logger.info(
                f"event : {event.__class__.__name__}, handler : {handler.func.__name__}, params : {event}"
            )
            try:
                handler(event)
            except Exception as e:
                if isinstance(e, exceptions.OperationalError):
                    logger.debug(f"Operational Error : {e}")
                    raise e
                logger.error(f"Unresolved Exception : {e}")
                raise exceptions.UnresolvedError(str(e))
            else:
                logger.info(f"handler : {handler.func.__name__} : completed")

    def handle_command(self, command: commands.Command):
        for handler in self.command_handlers[type(command)]:
            logger.info(
                f"command : {command.__class__.__name__}, handler : {handler.func.__name__}, params : {command}"
            )
            try:
                handler(command)
            except Exception as e:
                if isinstance(e, exceptions.OperationalError):
                    logger.debug(f"error : operational_error : {e}")
                    raise e
                logger.error(f"error : unresolved_exception : {e}")
                raise exceptions.UnresolvedError(str(e))
            else:
                logger.info(f"handler : {handler.func.__name__} : completed")
