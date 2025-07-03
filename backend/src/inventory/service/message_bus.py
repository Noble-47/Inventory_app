from collection import deque

from inventory.domain import events, commands
from inventory.service.uow import UnitOfWork

Message = Union[events.Event, commands.Command]


class MessageBus:

    def __init__(self, uow:UnitOfWork, command_handlers:dict[commands.Command, list[callable]], event_handlers: dict[events.Event, list[callable]]):
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.uow = uow

    def handle(self, message: Message):
        queue = deque()
        queue.append(message)
        while queue:
            if isinstance(message, commands.Command):
                self.handle_command(message, uow)
            if isinstance(message, events.Event):
                self.handle_events(message, uow)
            else:
                raise TypeError(f"Message must by of type {events.Event} or {commands.Command}. Got {type(message)}")

            queue.extend(self.uow.collect_events())

    def handle_events(self, event:events.Event, uow:Uow):
        handlers = self.event_handlers.get(type(event), list())
        for handler in handlers:
            handler(event)

    def handle_command(self, command:commands.Command, uow:Uow):
        handlers = self.command_handlers.get(type(command), list())
        for handler in handlers:
            handler(command, uow)
