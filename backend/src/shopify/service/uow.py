from shopify import db


class UnitOfWork:
    session_maker = db.db_session

    def __enter__(self):
        self.session = next(session_maker)
        self.prepare()
        return self

    def prepare(self):
        events = []
        self.business = db.Business(self.session, events)
        self.accounts = db.Account(self.session, events)
        self.shops = db.Shop(self.session, events)
        self.tokenizer = db.Tokenizer(self.session, events)
        self.audit = db.Audit(self.session, events)
        self.verification = db.AccountVerifier(self.session, events)
        self.registry = db.Registry(self.session, events)
        self.settings = db.Setting(self.session, events)
        self.events = events

    def __exit__(self):
        self.session.rollback()

    def commit(self):
        self.session.commit()

    def collect_events(self):
        return (event for event in self.events)
