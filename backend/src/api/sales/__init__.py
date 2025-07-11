from fastapi import FastAPI


def setup(app: FastAPI):

    from api.sales.router import router

    app.include_router(router)

    @app.on_event("startup")
    def on_startup():
        pass

    @app.get("/services/sales", tags=["Services"])
    def root():
        return {"message": "Sales service is running"}
