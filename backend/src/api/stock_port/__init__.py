from fastapi import FastAPI


def setup(app: FastAPI):

    from api.stock_port.router import router

    app.include_router(router)

    @app.on_event("startup")
    def on_startup():
        # create db tables
        pass

    @app.get("/services/orders", tags=["Services"])
    def root():
        return {"message": "Orders service is running"}
