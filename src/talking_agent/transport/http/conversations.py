import asyncio
from contextlib import suppress
from typing import cast

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from talking_agent.application.conversations import ConversationService
from talking_agent.transport.http.generated_contract import (
    CreateConversationResponse,
    ErrorResponse,
    SendMessageRequest,
    SendMessageResponse,
)

router = APIRouter(prefix="/v1/conversations")


def conversation_service(request: Request) -> ConversationService:
    return cast(ConversationService, request.app.state.conversation_service)


@router.post("", response_model=CreateConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(request: Request) -> CreateConversationResponse:
    conversation_id = await conversation_service(request).create()
    return CreateConversationResponse(conversation_id=conversation_id)


@router.post("/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message(
    conversation_id: str,
    payload: SendMessageRequest,
    request: Request,
) -> SendMessageResponse | JSONResponse:
    reply_task = asyncio.create_task(conversation_service(request).reply(conversation_id, payload.text))
    try:
        while not reply_task.done():
            if await request.is_disconnected():
                reply_task.cancel()
                with suppress(asyncio.CancelledError):
                    await reply_task
                raise asyncio.CancelledError
            await asyncio.sleep(0.01)
        reply = await reply_task
    except LookupError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(code="conversation_not_found").model_dump(),
        )
    except TimeoutError:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content=ErrorResponse(code="llm_timeout").model_dump(),
        )
    except RuntimeError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(code="llm_unavailable").model_dump(),
        )
    finally:
        if not reply_task.done():
            reply_task.cancel()
            with suppress(asyncio.CancelledError):
                await reply_task
    return SendMessageResponse(reply=reply)
