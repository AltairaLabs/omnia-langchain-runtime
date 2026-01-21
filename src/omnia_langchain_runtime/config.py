# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Configuration loading from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class ProviderType(str, Enum):
    """Supported LLM provider types."""

    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    MOCK = "mock"

    @classmethod
    def from_string(cls, value: str) -> "ProviderType":
        """Create from string value."""
        try:
            return cls(value.lower())
        except ValueError:
            valid = [t.value for t in cls]
            raise ValueError(f"Invalid provider type '{value}'. Must be one of: {valid}") from None


class SessionType(str, Enum):
    """Supported session store types."""

    MEMORY = "memory"
    REDIS = "redis"


@dataclass
class Config:
    """Runtime configuration loaded from environment variables."""

    # Agent identification
    agent_name: str
    namespace: str

    # PromptPack configuration
    promptpack_path: str = "/etc/omnia/pack/pack.json"
    promptpack_name: str = ""
    promptpack_namespace: str = ""
    prompt_name: str = "default"

    # Session configuration
    session_type: SessionType = SessionType.MEMORY
    session_url: str = ""
    session_ttl_seconds: int = 86400  # 24 hours

    # Provider configuration
    provider_type: ProviderType = ProviderType.MOCK
    provider_model: str = ""
    provider_base_url: str = ""
    provider_ref_name: str = ""
    provider_ref_namespace: str = ""

    # Context management
    context_window: int = 0  # 0 = no limit
    truncation_strategy: str = ""

    # Mock provider configuration
    mock_config_path: str = ""
    media_base_path: str = "/etc/omnia/media"

    # Tools configuration
    tools_config_path: str = ""

    # Server ports
    grpc_port: int = 9000
    health_port: int = 9001

    # Provider API keys (loaded from environment)
    api_keys: dict[str, str] = field(default_factory=dict)


class ConfigError(Exception):
    """Error in configuration."""


def load_config() -> Config:
    """Load configuration from environment variables.

    Returns:
        Config object with all settings.

    Raises:
        ConfigError: If required configuration is missing or invalid.
    """
    config = Config(
        agent_name=_get_required("OMNIA_AGENT_NAME"),
        namespace=_get_required("OMNIA_NAMESPACE"),
        promptpack_path=_get_or_default("OMNIA_PROMPTPACK_PATH", "/etc/omnia/pack/pack.json"),
        promptpack_name=os.getenv("OMNIA_PROMPTPACK_NAME", ""),
        promptpack_namespace=os.getenv("OMNIA_PROMPTPACK_NAMESPACE", ""),
        prompt_name=_get_or_default("OMNIA_PROMPT_NAME", "default"),
        session_type=_parse_session_type(os.getenv("OMNIA_SESSION_TYPE", "memory")),
        session_url=os.getenv("OMNIA_SESSION_URL", ""),
        session_ttl_seconds=_parse_int("OMNIA_SESSION_TTL", 86400),
        provider_type=_parse_provider_type(os.getenv("OMNIA_PROVIDER_TYPE", "mock")),
        provider_model=os.getenv("OMNIA_PROVIDER_MODEL", ""),
        provider_base_url=os.getenv("OMNIA_PROVIDER_BASE_URL", ""),
        provider_ref_name=os.getenv("OMNIA_PROVIDER_REF_NAME", ""),
        provider_ref_namespace=os.getenv("OMNIA_PROVIDER_REF_NAMESPACE", ""),
        context_window=_parse_int("OMNIA_CONTEXT_WINDOW", 0),
        truncation_strategy=os.getenv("OMNIA_TRUNCATION_STRATEGY", ""),
        mock_config_path=_get_or_default(
            "OMNIA_MOCK_CONFIG",
            os.getenv("OMNIA_PROVIDER_MOCK_CONFIG", ""),
        ),
        media_base_path=_get_or_default("OMNIA_MEDIA_BASE_PATH", "/etc/omnia/media"),
        tools_config_path=os.getenv("OMNIA_TOOLS_CONFIG", ""),
        grpc_port=_parse_int("OMNIA_GRPC_PORT", 9000),
        health_port=_parse_int("OMNIA_HEALTH_PORT", 9001),
    )

    # Load API keys from environment
    config.api_keys = {
        "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
        "openai": os.getenv("OPENAI_API_KEY", ""),
        "google": os.getenv("GOOGLE_API_KEY", ""),
    }

    # Validate configuration
    _validate_config(config)

    return config


def _get_required(name: str) -> str:
    """Get a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise ConfigError(f"{name} is required")
    return value


def _get_or_default(name: str, default: str) -> str:
    """Get an environment variable with a default."""
    return os.getenv(name) or default


def _parse_int(name: str, default: int) -> int:
    """Parse an integer environment variable."""
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError as e:
        raise ConfigError(f"Invalid {name}: must be an integer") from e


def _parse_provider_type(value: str) -> ProviderType:
    """Parse provider type from string."""
    try:
        return ProviderType.from_string(value)
    except ValueError as e:
        raise ConfigError(str(e)) from e


def _parse_session_type(value: str) -> SessionType:
    """Parse session type from string."""
    try:
        return SessionType(value.lower())
    except ValueError:
        valid = [t.value for t in SessionType]
        raise ConfigError(
            f"Invalid OMNIA_SESSION_TYPE '{value}'. Must be one of: {valid}"
        ) from None


def _validate_config(config: Config) -> None:
    """Validate configuration consistency."""
    # Redis session requires URL
    if config.session_type == SessionType.REDIS and not config.session_url:
        raise ConfigError("OMNIA_SESSION_URL is required when using Redis sessions")

    # Validate provider API keys for non-mock providers
    if config.provider_type == ProviderType.CLAUDE and not config.api_keys.get("anthropic"):
        raise ConfigError("ANTHROPIC_API_KEY is required for Claude provider")

    if config.provider_type == ProviderType.OPENAI and not config.api_keys.get("openai"):
        raise ConfigError("OPENAI_API_KEY is required for OpenAI provider")

    if config.provider_type == ProviderType.GEMINI and not config.api_keys.get("google"):
        raise ConfigError("GOOGLE_API_KEY is required for Gemini provider")
