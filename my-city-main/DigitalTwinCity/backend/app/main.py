from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.init_db import init_db
from app.db.seed import seed_database

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
    description="Digital Twin City backend with simulations, explainable AI analysis, hotspots, and Telegram alerts.",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_database()


app.include_router(api_router)