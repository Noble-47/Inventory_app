from fastapi import FastAPI

from analytics.db import create_tables


def setup(app: FastAPI):

    from api.analytics.router import router

    app.include_router(router)

    @app.on_event("startup")
    def on_startup():
        print("Creating tables")
        create_tables()

    @app.get("/services/analytics", tags=["Services"])
    def root():
        return {"message": "Analytics service is running"}
