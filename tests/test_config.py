# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Tests for configuration loading."""

import os
from unittest import mock

import pytest

from omnia_langchain_runtime.config import (
    Config,
    ConfigError,
    ProviderType,
    SessionType,
    load_config,
)


class TestLoadConfig:
    """Tests for load_config function."""

    def test_required_env_vars(self) -> None:
        """Test error when required env vars are missing."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigError) as exc_info:
                load_config()
            assert "OMNIA_AGENT_NAME" in str(exc_info.value)

    def test_minimal_config(self) -> None:
        """Test loading minimal configuration."""
        env = {
            "OMNIA_AGENT_NAME": "test-agent",
            "OMNIA_NAMESPACE": "default",
            "OMNIA_PROVIDER_TYPE": "mock",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            config = load_config()

        assert config.agent_name == "test-agent"
        assert config.namespace == "default"
        assert config.provider_type == ProviderType.MOCK
        assert config.session_type == SessionType.MEMORY

    def test_full_config(self) -> None:
        """Test loading full configuration."""
        env = {
            "OMNIA_AGENT_NAME": "test-agent",
            "OMNIA_NAMESPACE": "production",
            "OMNIA_PROMPTPACK_PATH": "/custom/pack.json",
            "OMNIA_PROMPT_NAME": "support",
            "OMNIA_SESSION_TYPE": "memory",
            "OMNIA_PROVIDER_TYPE": "mock",
            "OMNIA_PROVIDER_MODEL": "test-model",
            "OMNIA_GRPC_PORT": "8000",
            "OMNIA_HEALTH_PORT": "8001",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            config = load_config()

        assert config.promptpack_path == "/custom/pack.json"
        assert config.prompt_name == "support"
        assert config.provider_model == "test-model"
        assert config.grpc_port == 8000
        assert config.health_port == 8001

    def test_redis_session_requires_url(self) -> None:
        """Test Redis session requires URL."""
        env = {
            "OMNIA_AGENT_NAME": "test",
            "OMNIA_NAMESPACE": "default",
            "OMNIA_SESSION_TYPE": "redis",
            "OMNIA_PROVIDER_TYPE": "mock",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            with pytest.raises(ConfigError) as exc_info:
                load_config()
            assert "SESSION_URL" in str(exc_info.value)

    def test_invalid_provider_type(self) -> None:
        """Test error on invalid provider type."""
        env = {
            "OMNIA_AGENT_NAME": "test",
            "OMNIA_NAMESPACE": "default",
            "OMNIA_PROVIDER_TYPE": "invalid",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            with pytest.raises(ConfigError) as exc_info:
                load_config()
            assert "provider type" in str(exc_info.value).lower()

    def test_claude_requires_api_key(self) -> None:
        """Test Claude provider requires API key."""
        env = {
            "OMNIA_AGENT_NAME": "test",
            "OMNIA_NAMESPACE": "default",
            "OMNIA_PROVIDER_TYPE": "claude",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            with pytest.raises(ConfigError) as exc_info:
                load_config()
            assert "ANTHROPIC_API_KEY" in str(exc_info.value)


class TestProviderType:
    """Tests for ProviderType enum."""

    def test_from_string(self) -> None:
        """Test creating from string."""
        assert ProviderType.from_string("claude") == ProviderType.CLAUDE
        assert ProviderType.from_string("OPENAI") == ProviderType.OPENAI
        assert ProviderType.from_string("Mock") == ProviderType.MOCK

    def test_from_string_invalid(self) -> None:
        """Test error on invalid string."""
        with pytest.raises(ValueError):
            ProviderType.from_string("invalid")
