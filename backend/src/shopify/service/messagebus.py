from collections import deque
from typing import Annotated

from shopify.service.uow import UnitOfWork
from shopify.domain import commands
from shopify.domain import events

Message = Annotated[events.Event, commands.Command]

class MessageBus:

    def __init__(self, command_handlers: dict[str, list[callable]], event_handlers: dict[str, list[callable]], uow: UnitOfWork):
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

    def handle_event(self, event:events.Event):
        for handler in self.event_handlers.get(type(event), list()):
            print(f"Handling event : {event} with handler : {handler}")
            handler(event)

    def handle_command(self, command: commands.Command):
        for handler in self.command_handlers[type(command)]:
            print(f"Handling command : {command} with handler : {handler}")
            handler(command)
