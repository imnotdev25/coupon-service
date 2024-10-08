from fastapi import FastAPI

from app.lifetime import startup, shutdown
from app.base import router

app = FastAPI(title="Coupon Service")

app.add_event_handler("startup", startup(app))
app.add_event_handler("shutdown", shutdown(app))

app.include_router(router)
