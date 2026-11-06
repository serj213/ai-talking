import asyncio
import json

import httpx
import pytest

from talking_agent.application.conversations import (
    ConversationMessage,
    GenerateReplyRequest,
)
from talking_agent.infrastructure.deepseek_language_model import DeepSeekLanguageModel


def test_deepseek_adapter_sends_messages_and_token_limit() -> None:
    asyncio.run(deepseek_adapter_sends_messages_and_token_limit())


async def deepseek_adapter_sends_messages_and_token_limit() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-key"
        body = json.loads(request.content)
        assert body["model"] == "deepseek-flash"
        assert body["max_tokens"] == 120
        assert body["thinking"] == {"type": "disabled"}
        return httpx.Response(200, json={"choices": [{"message": {"content": "Hi!"}}]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.deepseek.com") as client:
        adapter = DeepSeekLanguageModel(client, "test-key", "deepseek-flash")
        reply = await adapter.generate(
            GenerateReplyRequest(messages=(ConversationMessage("user", "Hello"),))
        )

    assert reply == "Hi!"


def test_deepseek_adapter_normalizes_provider_error() -> None:
    asyncio.run(deepseek_adapter_normalizes_provider_error())


async def deepseek_adapter_normalizes_provider_error() -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(503))
    async with httpx.AsyncClient(transport=transport, base_url="https://api.deepseek.com") as client:
        adapter = DeepSeekLanguageModel(client, "test-key", "deepseek-flash")

        with pytest.raises(RuntimeError, match="DeepSeek request failed"):
            await adapter.generate(GenerateReplyRequest(messages=()))


def test_deepseek_adapter_normalizes_timeout() -> None:
    asyncio.run(deepseek_adapter_normalizes_timeout())


async def deepseek_adapter_normalizes_timeout() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("request timed out")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.deepseek.com") as client:
        adapter = DeepSeekLanguageModel(client, "test-key", "deepseek-flash")

        with pytest.raises(TimeoutError, match="DeepSeek request timed out"):
            await adapter.generate(GenerateReplyRequest(messages=()))


def test_deepseek_adapter_rejects_empty_reply() -> None:
    asyncio.run(deepseek_adapter_rejects_empty_reply())


async def deepseek_adapter_rejects_empty_reply() -> None:
    transport = httpx.MockTransport(
        lambda _: httpx.Response(200, json={"choices": [{"message": {"content": "  "}}]})
    )
    async with httpx.AsyncClient(transport=transport, base_url="https://api.deepseek.com") as client:
        adapter = DeepSeekLanguageModel(client, "test-key", "deepseek-flash")

        with pytest.raises(RuntimeError, match="DeepSeek returned an empty response"):
            await adapter.generate(GenerateReplyRequest(messages=()))


def test_deepseek_adapter_propagates_cancellation() -> None:
    asyncio.run(deepseek_adapter_propagates_cancellation())


async def deepseek_adapter_propagates_cancellation() -> None:
    request_started = asyncio.Event()
    response_allowed = asyncio.Event()

    async def handler(_: httpx.Request) -> httpx.Response:
        request_started.set()
        await response_allowed.wait()
        return httpx.Response(200, json={"choices": [{"message": {"content": "Hi!"}}]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url="https://api.deepseek.com") as client:
        adapter = DeepSeekLanguageModel(client, "test-key", "deepseek-flash")
        reply = asyncio.create_task(adapter.generate(GenerateReplyRequest(messages=())))
        await request_started.wait()
        reply.cancel()

        with pytest.raises(asyncio.CancelledError):
            await reply
