import asyncio
from contextlib import suppress

from talking_agent.application.conversations import ConversationService
from talking_agent.infrastructure.fake_language_model import FakeLanguageModel
from talking_agent.infrastructure.in_memory_conversation_store import (
    InMemoryConversationStore,
)


def test_service_keeps_context_inside_one_conversation() -> None:
    asyncio.run(keeps_context_inside_one_conversation())


async def keeps_context_inside_one_conversation() -> None:
    language_model = FakeLanguageModel()
    service = ConversationService(InMemoryConversationStore(), language_model)
    first_conversation = await service.create()
    second_conversation = await service.create()

    await service.reply(first_conversation, "I like hiking.")
    await service.reply(second_conversation, "I like cooking.")
    await service.reply(first_conversation, "What should I try next?")

    messages = language_model.requests[-1].messages

    assert [message.content for message in messages] == [
        "You are a friendly conversation partner helping the user practise American English. Reply in English with one to three short sentences and one natural question.",
        "I like hiking.",
        "This is a fake reply.",
        "What should I try next?",
    ]


def test_service_serializes_concurrent_turns_for_one_conversation() -> None:
    asyncio.run(serializes_concurrent_turns_for_one_conversation())


async def serializes_concurrent_turns_for_one_conversation() -> None:
    language_model = FakeLanguageModel(block_first_reply=True)
    service = ConversationService(InMemoryConversationStore(), language_model)
    conversation = await service.create()

    first_reply = asyncio.create_task(service.reply(conversation, "First message."))
    await language_model.first_request_started.wait()
    second_reply = asyncio.create_task(service.reply(conversation, "Second message."))
    language_model.allow_first_reply.set()
    await asyncio.gather(first_reply, second_reply)

    assert [message.content for message in language_model.requests[1].messages] == [
        "You are a friendly conversation partner helping the user practise American English. Reply in English with one to three short sentences and one natural question.",
        "First message.",
        "This is a fake reply.",
        "Second message.",
    ]


def test_cancelled_turn_is_not_added_to_conversation() -> None:
    asyncio.run(cancelled_turn_is_not_added_to_conversation())


async def cancelled_turn_is_not_added_to_conversation() -> None:
    language_model = FakeLanguageModel(block_first_reply=True)
    service = ConversationService(InMemoryConversationStore(), language_model)
    conversation = await service.create()

    cancelled_reply = asyncio.create_task(service.reply(conversation, "Do not save this."))
    await language_model.first_request_started.wait()
    cancelled_reply.cancel()

    with suppress(asyncio.CancelledError):
        await cancelled_reply

    await service.reply(conversation, "What remains in the context?")

    assert [message.content for message in language_model.requests[-1].messages] == [
        "You are a friendly conversation partner helping the user practise American English. Reply in English with one to three short sentences and one natural question.",
        "What remains in the context?",
    ]


def test_service_adds_prompt_and_limits_context() -> None:
    asyncio.run(service_adds_prompt_and_limits_context())


async def service_adds_prompt_and_limits_context() -> None:
    language_model = FakeLanguageModel()
    service = ConversationService(
        InMemoryConversationStore(), language_model, max_context_messages=4
    )
    conversation = await service.create()

    await service.reply(conversation, "First.")
    await service.reply(conversation, "Second.")
    await service.reply(conversation, "Third.")
    await service.reply(conversation, "Fourth.")

    messages = language_model.requests[-1].messages

    assert [message.role for message in messages] == [
        "system",
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
    ]
    assert [message.content for message in messages[1:]] == [
        "Second.",
        "This is a fake reply.",
        "Third.",
        "This is a fake reply.",
        "Fourth.",
    ]
