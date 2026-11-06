from pathlib import Path

import pytest
from pydantic import ValidationError

from talking_agent.settings import AppSettings


def test_settings_reads_declared_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    settings = AppSettings()

    assert settings.environment == "test"


def test_settings_rejects_unknown_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "unknown")

    with pytest.raises(ValidationError):
        AppSettings()


def test_readme_documents_available_commands() -> None:
    readme = (Path(__file__).parent.parent / "README.md").read_text()

    assert "uv run talking-agent" in readme
    assert "make gen-openapi" in readme
    assert "make check" in readme
