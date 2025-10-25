from fastapi import FastAPI

from debt_tracker.db import create_tables


def setup(app: FastAPI):

    from api.debt_tracker.router import router

    app.include_router(router)

    @app.on_event("startup")
    def on_startup():
        create_tables()

    @app.get("/services/tracker", tags=["Services"])
    def root():
        return {"message": "Debt Tracker service is running"}
