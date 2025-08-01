from fastapi import FastAPI

from stock_port.db import db


def setup(app: FastAPI):

    from api.stock_port.router import router

    app.include_router(router)

    @app.on_event("startup")
    def on_startup():
        # create db tables
        db.create_tables()

    @app.get("/services/orders", tags=["Services"])
    def root():
        return {"message": "Orders service is running"}
