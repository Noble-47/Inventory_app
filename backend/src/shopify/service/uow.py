from shopify import db


class UnitOfWork:
    def __init__(self, session_maker=db.db_session):
        self.session_maker = session_maker

    def __enter__(self):
        self.session = next(self.session_maker())
        self.prepare()
        return self

    def prepare(self):
        events = []
        self.views = db.View(self.session)
        self.business = db.Business(self.session, events)
        self.accounts = db.Account(self.session, events)
        self.shops = db.Shop(self.session, events)
        self.tokenizer = db.Tokenizer(self.session, events)
        self.audit = db.Audit(self.session, events)
        self.verification = db.AccountVerifier(self.session, events)
        self.registry = db.Registry(self.session, events)
        self.settings = db.Setting(self.session, events)
        self.events = events

    def __exit__(self, *args, **kwargs):
        self.session.rollback()

    def commit(self):
        for business in self.business.seen:
            self.events.extend(business.events)
            business.events.clear()
        self.session.commit()

    def collect_events(self):
        for event in self.events:
            yield event
        self.events.clear()
