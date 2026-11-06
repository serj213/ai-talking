from importlib.metadata import entry_points
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from talking_agent.application.health import HealthService
from talking_agent.main import create_app, main


def test_health_service_returns_ok() -> None:
    assert HealthService().status() == "ok"


def test_health_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_main_rejects_invalid_environment_before_starting_server(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "unknown")

    with patch("talking_agent.main.uvicorn.run") as run, pytest.raises(ValidationError):
        main()

    run.assert_not_called()


def test_installed_console_script_targets_application_main() -> None:
    scripts = entry_points(group="console_scripts")
    script = next(item for item in scripts if item.name == "talking-agent")

    assert script.value == "talking_agent.main:main"
