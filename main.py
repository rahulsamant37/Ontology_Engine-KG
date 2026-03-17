from __future__ import annotations

from fastapi import FastAPI

from api.routes import router
from utils.config import settings
from utils.logging import configure_logging

configure_logging()

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
