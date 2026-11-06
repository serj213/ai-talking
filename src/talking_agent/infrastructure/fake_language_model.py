import asyncio

from talking_agent.application.conversations import GenerateReplyRequest


class FakeLanguageModel:
    def __init__(self, block_first_reply: bool = False) -> None:
        self.requests: list[GenerateReplyRequest] = []
        self.first_request_started = asyncio.Event()
        self.allow_first_reply = asyncio.Event()
        self._block_first_reply = block_first_reply

    async def generate(self, request: GenerateReplyRequest) -> str:
        self.requests.append(request)
        if self._block_first_reply and len(self.requests) == 1:
            self.first_request_started.set()
            await self.allow_first_reply.wait()
        return "This is a fake reply."
