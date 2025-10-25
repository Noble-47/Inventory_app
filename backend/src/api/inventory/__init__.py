from fastapi import FastAPI

from inventory.adapters import orm
from inventory.bootstrap import bootstrap

bus = bootstrap()


def setup(app: FastAPI):

    from api.inventory.router import router

    app.include_router(router)

    @app.on_event("startup")
    def on_startup():
        orm.create_tables()

    @app.get("/services/inventory", tags=["Services"])
    def root():
        return {"message": "Inventory service is running."}
