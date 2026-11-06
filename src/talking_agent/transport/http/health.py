from fastapi import APIRouter

from talking_agent.application.health import HealthService
from talking_agent.transport.http.generated_contract import (
    HEALTH_PATH,
    HEALTH_STATUS_CODE,
    HealthResponse,
)

router = APIRouter()


@router.get(HEALTH_PATH, response_model=HealthResponse, status_code=HEALTH_STATUS_CODE)
async def health() -> HealthResponse:
    return HealthResponse(status=HealthService().status())
