from __future__ import annotations

from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

from shared import datetime_now_func, get_rotating_logger


logger = get_rotating_logger("exchange", "exchange.log")


def do_nothing(*args, **kwargs):
    pass


@dataclass
class Service:
    name: str

    def __hash__(self):
        return hash(self.name)


@dataclass
class Recipient:
    subject: str
    service: str
    handler: Callable[Any, None] = field(default=do_nothing)  # Do nothing fallback

    def __hash__(self):
        return hash((self.service, self.subject))


@dataclass
class Subject:
    id: Optional[int] = None
    name: str = ""
    recipients: list[Recipient] = field(default_factory=set)

    def __hash__(self):
        return hash(self.name)


@dataclass
class Channel:
    service: str
    name: str
    subjects: set[Subject] = field(default_factory=set)

    def __hash__(self):
        return hash(self.name)


@dataclass
class Receiver:
    recipient: Recipient
    message: "Message"
    acknowledged: bool = False

    def acknowledge(self):
        # if callable(self.recipient.handler)
        logger.info(
            f"[ACK] Acknowledging Message {self.message.subject} - {self.recipient.service}"
        )
        handler = self.recipient.handler
        logger.info(f"[AKC] Handler: {handler.__name__}")
        handler(**self.message.data)
        self.acknowledged = True


@dataclass
class Message:
    id: Optional[int] = None
    subject: str = ""
    data: dict = field(default_factory=dict)
    payload: str | None = None
    time: datetime = field(default_factory=datetime_now_func)
    receivers: list[Receiver] = field(default_factory=list)

    def __post_init__(self):
        if self.data and (self.payload is None):
            self.payload = json.dumps(self.data)

    def __hash__(self):
        return hash(self.id)
