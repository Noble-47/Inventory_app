import asyncio

from exchange.models import Service, Channel, Message, Recipient, Receiver, Subject
from exchange.db import CollectionSet


class Router:

    def __init__(self, session):
        self.session = session
        self.services = CollectionSet(Service, session)
        self.channels = CollectionSet(Channel, session)
        self.subjects = CollectionSet(Subject, session)
        self.messages = CollectionSet(Message, session)
        self.recipients = CollectionSet(Recipient, session)

    @property
    def channel_list(self):
        return [channel.name for channel in self.channels]

    @property
    def subject_list(self):
        return [subject.name for subject in self.subjects]

    @property
    def service_list(self):
        return [service.name for service in self.services]

    async def broadcast(self, message: Message):
        if not (message.subject in self.subject_list):
            print(f"[-] Message Subject Is Not Recognized - {message.subject}")
            return
        subject = next(
            subject for subject in self.subjects if subject.name == message.subject
        )
        for recipient in subject.recipients:
            print(f"[-] Routing Message to - {recipient.service}")
            receiver = Receiver(recipient=recipient, message=message)
            message.receivers.append(receiver)
            self.session.add(receiver)
        # self.session.add(message)
        for receiver in message.receivers:
            # try:
            receiver.acknowledge()
            # except Exception as e:
            #    print(e)
        # await asyncio.gather(
        #    *[self.safe_ack(ack) for ack in message.recievers],
        # )
        print("[o] Updating Record")
        self.session.commit()

    async def safe_ack(self, ack):
        try:
            await asyncio.to_thread(ack.acknowledge)
        except Exception as e:
            print("[ERROR] Failed To Acknowledge Message")

    def add_recipient(self, service: str, subject: str, handler: callable):
        if subject not in self.subject_list:
            return
        subject = next(obj for obj in self.subjects if obj.name == subject)
        recipient = next(
            (
                recipient
                for recipient in self.recipients
                if recipient.service == service and recipient.subject == subject.name
            ),
            Recipient(subject=subject, service=service),
        )
        recipient.handler = handler
        subject.recipients.add(recipient)
        self.session.commit()

    def add_sender(self, service, channel, subject):
        service = next(
            (obj for obj in self.services if obj.name == service), Service(name=service)
        )
        channel = next(
            (obj for obj in self.channels if obj.name == channel),
            Channel(service=service.name, name=channel),
        )
        if subject not in self.subject_list:
            channel.subjects.add(Subject(name=subject))
        self.services.add(service)
        self.channels.add(channel)
        self.session.commit()
