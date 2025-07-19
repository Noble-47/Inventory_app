from typing import Union

from sqlalchemy import Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy import Table, Column, create_engine
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select

from exchange.models import Service, Channel, Subject, Message, Recipient, Receiver
from exchange import config

Model = Union[Service, Channel, Subject, Message, Recipient, Receiver]

mapper_registry = registry()
metadata = mapper_registry.metadata

service_table = Table("services", metadata, Column("name", String, primary_key=True))

channel_table = Table(
    "channels",
    metadata,
    Column("name", String, primary_key=True),
    Column("service", ForeignKey("services.name")),
)


subject_table = Table(
    "subjects",
    metadata,
    Column("name", String, primary_key=True),
    Column("channel", ForeignKey("channels.name")),
)

message_table = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("subject", ForeignKey("subjects.name")),
    Column("payload", String),
    Column("time", DateTime),
)


recipients_table = Table(
    "recipients",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("subject", ForeignKey("subjects.name")),
    Column("service", ForeignKey("services.name")),
    UniqueConstraint("subject", "service", name="idx_unique_service_subject_handler"),
)


receivers_table = Table(
    "receivers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("recipient_id", ForeignKey("recipients.id")),
    Column("message_id", ForeignKey("messages.id")),
    Column("acknowledged", Integer, default=0),
)


def start_mappers():
    mapper_registry.map_imperatively(Service, service_table)
    mapper_registry.map_imperatively(
        Channel,
        channel_table,
        properties={"subjects": relationship(Subject, collection_class=set)},
    )
    mapper_registry.map_imperatively(
        Subject,
        subject_table,
        properties={"recipients": relationship(Recipient, collection_class=set)},
    )
    mapper_registry.map_imperatively(
        Message,
        message_table,
        properties={"recievers": relationship(Receiver, back_populates="message")},
    )
    mapper_registry.map_imperatively(
        Recipient,
        recipients_table,
        # properties = {"subject" : relationship(Subject)}
    )
    mapper_registry.map_imperatively(
        Receiver,
        receivers_table,
        properties={
            "message": relationship(Message),
            "recipient": relationship(Recipient),
        },
    )


engine = create_engine(config.database_url)


def create_tables():
    metadata.create_all(engine)


def db_session():
    with Session(engine) as session:
        yield session


class CollectionSet:

    def __init__(self, model: Model, session):
        self.session = session
        models = session.scalars(select(model)).all()
        self.object_set = set(models)

    def add(self, obj):
        if obj in self.object_set:
            return
        self.object_set.add(obj)
        self.session.add(obj)

    def __iter__(self):
        return iter(self.object_set)

    def __len__(self):
        return len(self.object_set)
