from fastapi import FastAPI


def setup(app: FastAPI):

    from api.debt_tracker.router import router

    app.include_router(router)

    @app.on_event("startup")
    def on_startup():
        pass

    @app.get("services/tracker", tags=["Services"])
    def root():
        return {"message": "Debt Tracker service is running"}
