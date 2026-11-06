from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from talking_agent.application.conversations import ConversationService
from talking_agent.infrastructure.deepseek_language_model import DeepSeekLanguageModel
from talking_agent.infrastructure.fake_language_model import FakeLanguageModel
from talking_agent.infrastructure.in_memory_conversation_store import (
    InMemoryConversationStore,
)
from talking_agent.settings import AppSettings
from talking_agent.transport.http.conversations import router as conversations_router
from talking_agent.transport.http.generated_contract import ErrorResponse
from talking_agent.transport.http.health import router as health_router


def create_app(settings: AppSettings | None = None) -> FastAPI:
    settings = settings or AppSettings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if settings.llm_provider == "fake":
            app.state.conversation_service = ConversationService(
                InMemoryConversationStore(),
                FakeLanguageModel(),
                settings.llm_max_context_messages,
            )
            yield
            return
        async with httpx.AsyncClient(
            base_url=settings.deepseek_base_url,
            timeout=settings.llm_timeout_seconds,
        ) as client:
            api_key = settings.deepseek_api_key
            if api_key is None:
                raise RuntimeError("DeepSeek API key is missing")
            app.state.conversation_service = ConversationService(
                InMemoryConversationStore(),
                DeepSeekLanguageModel(
                    client,
                    api_key.get_secret_value(),
                    settings.deepseek_model,
                    settings.llm_max_output_tokens,
                ),
                settings.llm_max_context_messages,
            )
            yield

    app = FastAPI(title="Talking Agent API", version="0.1.0", lifespan=lifespan)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, __: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(code="validation_error").model_dump(),
        )

    app.include_router(health_router)
    app.include_router(conversations_router)
    return app


def main() -> None:
    settings = AppSettings()
    app = create_app(settings)
    uvicorn.run(app, host="0.0.0.0", port=8000)
