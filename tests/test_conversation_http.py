import asyncio
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from talking_agent.application.conversations import ConversationService
from talking_agent.infrastructure.fake_language_model import FakeLanguageModel
from talking_agent.infrastructure.in_memory_conversation_store import (
    InMemoryConversationStore,
)
from talking_agent.main import create_app
from talking_agent.settings import AppSettings
from talking_agent.transport.http.conversations import SendMessageRequest, send_message


def test_client_can_create_conversation_and_send_message() -> None:
    with TestClient(create_app(AppSettings(_env_file=None))) as client:
        created = client.post("/v1/conversations")

        assert created.status_code == 201
        conversation_id = created.json()["conversation_id"]

        replied = client.post(
            f"/v1/conversations/{conversation_id}/messages",
            json={"text": "Hello!"},
        )

        assert replied.status_code == 200
        assert replied.json() == {"reply": "This is a fake reply."}


def test_client_receives_validation_and_not_found_errors() -> None:
    with TestClient(create_app(AppSettings(_env_file=None))) as client:
        invalid = client.post("/v1/conversations/missing/messages", json={"text": ""})
        missing = client.post("/v1/conversations/missing/messages", json={"text": "Hello!"})

    assert invalid.status_code == 422
    assert missing.status_code == 404
    assert invalid.json() == {"code": "validation_error"}
    assert missing.json() == {"code": "conversation_not_found"}


def test_disconnect_cancels_language_model_request() -> None:
    asyncio.run(disconnect_cancels_language_model_request())


async def disconnect_cancels_language_model_request() -> None:
    language_model = FakeLanguageModel(block_first_reply=True)
    service = ConversationService(InMemoryConversationStore(), language_model)
    conversation_id = await service.create()

    async def disconnected() -> bool:
        return language_model.first_request_started.is_set()

    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(conversation_service=service)),
        is_disconnected=disconnected,
    )

    with pytest.raises(asyncio.CancelledError):
        await send_message(conversation_id, SendMessageRequest(text="Hello!"), request)

    await service.reply(conversation_id, "What remains?")

    assert [message.content for message in language_model.requests[-1].messages] == [
        "You are a friendly conversation partner helping the user practise American English. Reply in English with one to three short sentences and one natural question.",
        "What remains?",
    ]
