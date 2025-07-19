from dataclasses import dataclass, field
from collections import deque
import requests
import asyncio
import json

from exchange import config


def publish(channel, subject, payload):
    url = config.root_url + f"/{channel}/{subject}"
    print(f"[x] [{channel}] Sending To {subject} - {payload}")
    try:
        r = requests.post(url, json=payload, timeout=3)
    except requests.exceptions.Timeout:
        print("The request timed out!")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


class Sender:

    def __init__(self, channel: str, subject):
        self.channel = channel
        self.subject = subject

    def __hash__(self):
        return hash((self.channel, self.subject))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.channel == other.channel
        return NotImplemented


class Receiver:

    def __init__(self, subject: str, handler: callable):
        self.handler = handler
        self.subject = subject

    def __hash__(self):
        return hash(self.subject)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.subject == other.subject
        return NotImplemented


class Exchange:

    def __init__(self, service: str, hub=None):
        self.service = service
        self.hub = hub

    @property
    def senders(self):
        return self.hub.senders[self.service]

    @property
    def receivers(self):
        return self.hub.receivers[self.service]

    def establish_channel(self, channel: str, subjects: list):
        for subject in subjects:
            sender = Sender(channel, subject)
            self.senders.add(sender)

    def listen_on(self, subject: str, handler: callable):
        receiver = Receiver(subject, handler)
        self.receivers.add(receiver)


class Hub:

    def __init__(self, router):
        self.receivers = {}
        self.senders = {}
        self.router = router

    def create_exchange(self, service: str):
        self.receivers[service] = set()
        self.senders[service] = set()
        return Exchange(service, self)

    def begin(self):
        for service, senders in self.senders.items():
            for sender in senders:
                self.router.add_sender(service, sender.channel, sender.subject)
        for service, receivers in self.receivers.items():
            for receiver in receivers:
                self.router.add_recipient(service, receiver.subject, receiver.handler)

    async def push(self, message):
        print(f"[-] Message Added To Hub - {message.subject}")
        await self.router.broadcast(message)
