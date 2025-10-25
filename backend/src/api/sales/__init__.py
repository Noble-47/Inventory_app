from fastapi import FastAPI

from sales.db import create_tables


def setup(app: FastAPI):

    from api.sales.router import router

    app.include_router(router)

    @app.on_event("startup")
    def on_startup():
        create_tables()

    @app.get("/services/sales", tags=["Services"])
    def root():
        return {"message": "Sales service is running"}
