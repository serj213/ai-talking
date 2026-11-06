import asyncio
from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

SYSTEM_PROMPT = (
    "You are a friendly conversation partner helping the user practise American English. "
    "Reply in English with one to three short sentences and one natural question."
)

@dataclass(frozen=True)
class ConversationMessage:
    role: str
    content: str


@dataclass(frozen=True)
class GenerateReplyRequest:
    messages: tuple[ConversationMessage, ...]


class LanguageModel(Protocol):
    async def generate(self, request: GenerateReplyRequest) -> str: ...


class ConversationStore(Protocol):
    async def create(self, conversation_id: str) -> None: ...

    async def get_messages(self, conversation_id: str) -> tuple[ConversationMessage, ...]: ...

    async def append(self, conversation_id: str, messages: tuple[ConversationMessage, ...]) -> None: ...


class ConversationService:
    def __init__(
        self,
        store: ConversationStore,
        language_model: LanguageModel,
        max_context_messages: int = 20,
    ) -> None:
        self._store = store
        self._language_model = language_model
        self._max_context_messages = max_context_messages
        self._locks: dict[str, asyncio.Lock] = {}

    async def create(self) -> str:
        conversation_id = str(uuid4())
        await self._store.create(conversation_id)
        self._locks[conversation_id] = asyncio.Lock()
        return conversation_id

    async def reply(self, conversation_id: str, text: str) -> str:
        lock = self._locks.get(conversation_id)
        if lock is None:
            raise LookupError("conversation not found")
        async with lock:
            messages = await self._store.get_messages(conversation_id)
            user_message = ConversationMessage(role="user", content=text)
            reply = await self._language_model.generate(
                GenerateReplyRequest(
                    messages=(ConversationMessage(role="system", content=SYSTEM_PROMPT),)
                    + messages[-self._max_context_messages :]
                    + (user_message,)
                )
            )
            assistant_message = ConversationMessage(role="assistant", content=reply)
            await self._store.append(conversation_id, (user_message, assistant_message))
            return reply
