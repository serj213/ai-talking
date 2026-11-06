from typing import Literal

from pydantic import BaseModel, ConfigDict

HEALTH_PATH = "/health"

HEALTH_STATUS_CODE = 200

class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
