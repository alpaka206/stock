from fastapi import FastAPI

from app.config import get_settings
from app.routers import history, overview, radar, stocks

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(overview.router)
app.include_router(radar.router)
app.include_router(stocks.router)
app.include_router(history.router)
