from pathlib import Path

import pytest
from pydantic import ValidationError

from talking_agent.settings import AppSettings


def test_settings_reads_declared_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    settings = AppSettings(_env_file=None)

    assert settings.environment == "test"


def test_settings_rejects_unknown_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "unknown")

    with pytest.raises(ValidationError):
        AppSettings(_env_file=None)


def test_settings_define_deepseek_timeout_and_output_limit() -> None:
    settings = AppSettings(_env_file=None)

    assert settings.llm_timeout_seconds == 10
    assert settings.llm_max_output_tokens == 120
    assert settings.llm_max_context_messages == 20


def test_settings_reads_api_keys_from_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "APP_ENV=test\n"
        "OPENAI_API_KEY=openai-test-key\n"
        "DEEPSEEK_API_KEY=deepseek-test-key\n"
    )
    monkeypatch.chdir(tmp_path)

    settings = AppSettings()

    assert settings.environment == "test"
    assert settings.openai_api_key is not None
    assert settings.openai_api_key.get_secret_value() == "openai-test-key"
    assert settings.deepseek_api_key is not None
    assert settings.deepseek_api_key.get_secret_value() == "deepseek-test-key"


def test_settings_reads_deepseek_key_from_local_dotenv_alias(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("DEEPSEEK_API_KEY!=deepseek-test-key\n")
    monkeypatch.chdir(tmp_path)

    settings = AppSettings()

    assert settings.deepseek_api_key is not None
    assert settings.deepseek_api_key.get_secret_value() == "deepseek-test-key"


def test_settings_use_fake_language_model_by_default() -> None:
    settings = AppSettings(_env_file=None)

    assert settings.llm_provider == "fake"


def test_settings_require_deepseek_key_for_deepseek_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(ValidationError, match="DEEPSEEK_API_KEY is required"):
        AppSettings(_env_file=None)


def test_readme_documents_available_commands() -> None:
    readme = (Path(__file__).parent.parent / "README.md").read_text()

    assert "uv run talking-agent" in readme
    assert "make gen-openapi" in readme
    assert "make check" in readme
