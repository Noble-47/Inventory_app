from collections import deque
from typing import Union

from inventory.domain import events, commands
from inventory.service.uow import UnitOfWork

Message = Union[events.Event, commands.Command]


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
            # elif issubclass(message, commands.Command):
            #    raise ValueError("You passed in the class instead of an instance")
            else:
                raise TypeError(
                    f"Message must by of type {events.Event} or {commands.Command}. Got {type(message)}"
                )

            queue.extend(self.uow.collect_new_events())
            print(queue)

    def handle_events(self, event: events.Event):
        handlers = self.event_handlers.get(type(event), list())
        print(f"Received Event: {event!r}")
        for handler in handlers:
            print(f"Handling Event {event!r} with {handler!r}")
            handler(event)
            print("Done")

    def handle_command(self, command: commands.Command):
        handlers = self.command_handlers.get(type(command), list())
        print(f"Received Command: {command!r}")
        for handler in handlers:
            print(f"Handling Command {command!r} with {handler!r}")
            handler(command)
            print("Done")
