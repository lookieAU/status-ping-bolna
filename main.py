from fastapi import FastAPI, Request
import uvicorn
from api.challenge import router as challenge_router
from api.status import router as status_router
import logging
import sys
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from services.rss_monitor import RSSMonitorService
import asyncio
from contextlib import asynccontextmanager

rss_monitor = RSSMonitorService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(rss_monitor.start(interval_seconds=60))
    yield
    task.cancel()


app = FastAPI(
    title="Bolna LLM Status Event API",
    description="API for receiving status events from LLM",
    version="0.0.1",
    lifespan=lifespan,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Exception: {exc}")
    return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/")
async def status_endpoint():
    return {"status": "ok", "message": "Bolna SMTP Webhook API is running"}


app.include_router(challenge_router)
app.include_router(status_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
