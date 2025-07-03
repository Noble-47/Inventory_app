from fastapi import FastAPI

from inventory.adapters import orm


def setup(app: FastAPI):

    from api.inventory.router import router

    app.include_router(router)

    @app.on_event("startup")
    def on_startup():
        orm.create_tables
        orm.start_mappers()
