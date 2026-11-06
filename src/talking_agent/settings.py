from typing import Literal

from pydantic import AliasChoices, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        validate_by_name=True,
    )

    environment: Literal["development", "test", "production"] = Field(
        default="development",
        validation_alias="APP_ENV",
    )
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
    )
    deepseek_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("DEEPSEEK_API_KEY!", "DEEPSEEK_API_KEY"),
    )
    llm_provider: Literal["fake", "deepseek"] = Field(
        default="fake",
        validation_alias="LLM_PROVIDER",
    )
    deepseek_model: str = Field(
        default="deepseek-flash",
        validation_alias="DEEPSEEK_MODEL",
    )
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        validation_alias="DEEPSEEK_BASE_URL",
    )
    llm_timeout_seconds: float = Field(
        default=10,
        gt=0,
        validation_alias="LLM_TIMEOUT_SECONDS",
    )
    llm_max_output_tokens: int = Field(
        default=120,
        gt=0,
        validation_alias="LLM_MAX_OUTPUT_TOKENS",
    )
    llm_max_context_messages: int = Field(
        default=20,
        gt=0,
        validation_alias="LLM_MAX_CONTEXT_MESSAGES",
    )

    @model_validator(mode="after")
    def validate_deepseek_key(self) -> "AppSettings":
        if self.llm_provider == "deepseek" and (
            self.deepseek_api_key is None
            or not self.deepseek_api_key.get_secret_value()
        ):
            raise ValueError("DEEPSEEK_API_KEY is required when LLM_PROVIDER is deepseek")
        return self
