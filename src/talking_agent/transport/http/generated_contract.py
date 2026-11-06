from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

HEALTH_PATH = "/health"

HEALTH_STATUS_CODE = 200

class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]

class CreateConversationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_id: str

class SendMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=1000)

class SendMessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reply: str

class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
