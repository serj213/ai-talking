import httpx

from talking_agent.application.conversations import GenerateReplyRequest


class DeepSeekLanguageModel:
    def __init__(
        self,
        client: httpx.AsyncClient,
        api_key: str,
        model: str,
        max_output_tokens: int = 120,
    ) -> None:
        self._client = client
        self._api_key = api_key
        self._model = model
        self._max_output_tokens = max_output_tokens

    async def generate(self, request: GenerateReplyRequest) -> str:
        try:
            response = await self._client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "messages": [
                        {"role": message.role, "content": message.content}
                        for message in request.messages
                    ],
                    "max_tokens": self._max_output_tokens,
                    "thinking": {"type": "disabled"},
                    "stream": False,
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        except httpx.TimeoutException as exc:
            raise TimeoutError("DeepSeek request timed out") from exc
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("DeepSeek request failed") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("DeepSeek returned an empty response")
        return content.strip()
