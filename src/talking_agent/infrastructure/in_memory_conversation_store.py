import asyncio
from dataclasses import dataclass, field

from talking_agent.application.conversations import ConversationMessage


@dataclass
class Conversation:
    messages: list[ConversationMessage] = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class InMemoryConversationStore:
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}

    async def create(self, conversation_id: str) -> None:
        self._conversations[conversation_id] = Conversation()

    async def get_messages(self, conversation_id: str) -> tuple[ConversationMessage, ...]:
        conversation = self._conversations[conversation_id]
        async with conversation.lock:
            return tuple(conversation.messages)

    async def append(self, conversation_id: str, messages: tuple[ConversationMessage, ...]) -> None:
        conversation = self._conversations[conversation_id]
        async with conversation.lock:
            conversation.messages.extend(messages)
