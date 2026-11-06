import uvicorn
from fastapi import FastAPI

from talking_agent.settings import AppSettings
from talking_agent.transport.http.health import router as health_router


def create_app(settings: AppSettings | None = None) -> FastAPI:
    settings = settings or AppSettings()
    app = FastAPI(title="Talking Agent API", version="0.1.0")
    app.include_router(health_router)
    return app


def main() -> None:
    settings = AppSettings()
    app = create_app(settings)
    uvicorn.run(app, host="0.0.0.0", port=8000)
