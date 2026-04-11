from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.dependencies import get_prompt_loader
from app.routers import calendar, history, news, overview, radar, stocks
from app.services.readiness import ProbeMode, build_readiness_report

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


@app.get("/readyz", tags=["health"])
async def readiness(probe: ProbeMode = Query(default="config")) -> JSONResponse:
    ready, report = await build_readiness_report(
        settings=settings,
        prompt_loader=get_prompt_loader(),
        probe=probe,
    )
    status_code = 200 if ready else 503
    return JSONResponse(status_code=status_code, content=report)


app.include_router(overview.router)
app.include_router(radar.router)
app.include_router(stocks.router)
app.include_router(history.router)
app.include_router(news.router)
app.include_router(calendar.router)
