import json
from pathlib import Path

from fastapi.routing import APIRoute

from talking_agent.main import create_app
from talking_agent.transport.http.generated_contract import HEALTH_STATUS_CODE
from talking_agent.transport.http.health import router as health_router


def test_runtime_openapi_matches_source_contract() -> None:
    source = json.loads((Path(__file__).parent.parent / "openapi/openapi.yaml").read_text())
    runtime = create_app().openapi()

    assert runtime["paths"]["/health"] == source["paths"]["/health"]
    assert runtime["components"]["schemas"]["HealthResponse"] == source["components"]["schemas"]["HealthResponse"]
    assert HEALTH_STATUS_CODE == 200


def test_health_route_uses_generated_status_code() -> None:
    route = next(
        route
        for route in health_router.routes
        if isinstance(route, APIRoute) and route.path == "/health"
    )

    assert route.status_code == HEALTH_STATUS_CODE
