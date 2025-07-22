from collections import deque
from typing import Union

from inventory.domain import events, commands
from inventory.service.uow import UnitOfWork
from shared import get_rotating_logger

Message = Union[events.Event, commands.Command]

logger = get_rotating_logger("inventory", "inventory.log")


class MessageBus:

    def __init__(
        self,
        uow: UnitOfWork,
        command_handlers: dict[commands.Command, list[callable]],
        event_handlers: dict[events.Event, list[callable]],
    ):
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.uow = uow

    def handle(self, message: Message):
        queue = deque()
        queue.append(message)
        while queue:
            message = queue.popleft()
            if isinstance(message, commands.Command):
                self.handle_command(message)
            elif isinstance(message, events.Event):
                self.handle_events(message)
            else:
                raise TypeError(
                    f"Message must by of type {events.Event} or {commands.Command}. Got {type(message)}"
                )

            queue.extend(self.uow.collect_new_events())

    def handle_events(self, event: events.Event):
        handlers = self.event_handlers.get(type(event), list())
        logger.info(f"Received Event: {event!r}")
        for handler in handlers:
            logger.info(f"Handling Event {event!r} with {handler!r}")
            try:
                handler(event)
            except Exception as e:
                logger.error("Error : {e}")
            else:
                logger.info("Done")

    def handle_command(self, command: commands.Command):
        handlers = self.command_handlers.get(type(command), list())
        logger.info(f"Received Command: {command!r}")
        for handler in handlers:
            logger.info(f"Handling Command {command!r} with {handler!r}")
            try:
                handler(command)
            except Exception as e:
                logger.error(f"Error : {e}")
            else:
                logger.info("Done")
