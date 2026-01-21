# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""LLM provider factory for creating language models."""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel

from omnia_langchain_runtime.config import Config, ProviderType

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Error creating or using a provider."""


def create_provider(config: Config, **kwargs: Any) -> BaseChatModel:
    """Create an LLM provider based on configuration.

    Args:
        config: Runtime configuration.
        **kwargs: Additional provider-specific arguments.

    Returns:
        A LangChain chat model.

    Raises:
        ProviderError: If provider creation fails.
    """
    provider_type = config.provider_type

    logger.info(
        "Creating provider",
        extra={"type": provider_type.value, "model": config.provider_model},
    )

    if provider_type == ProviderType.CLAUDE:
        return _create_claude_provider(config, **kwargs)

    if provider_type == ProviderType.OPENAI:
        return _create_openai_provider(config, **kwargs)

    if provider_type == ProviderType.GEMINI:
        return _create_gemini_provider(config, **kwargs)

    if provider_type == ProviderType.OLLAMA:
        return _create_ollama_provider(config, **kwargs)

    if provider_type == ProviderType.MOCK:
        return _create_mock_provider(config, **kwargs)

    raise ProviderError(f"Unknown provider type: {provider_type}")


def _create_claude_provider(config: Config, **kwargs: Any) -> BaseChatModel:
    """Create a Claude (Anthropic) provider."""
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError as e:
        raise ProviderError(
            "langchain-anthropic is required for Claude provider. "
            "Install with: pip install langchain-anthropic"
        ) from e

    model = config.provider_model or "claude-sonnet-4-20250514"
    api_key = config.api_keys.get("anthropic")

    provider_kwargs: dict[str, Any] = {
        "model": model,
        "api_key": api_key,
        **kwargs,
    }

    if config.provider_base_url:
        provider_kwargs["base_url"] = config.provider_base_url

    return ChatAnthropic(**provider_kwargs)


def _create_openai_provider(config: Config, **kwargs: Any) -> BaseChatModel:
    """Create an OpenAI provider."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as e:
        raise ProviderError(
            "langchain-openai is required for OpenAI provider. "
            "Install with: pip install langchain-openai"
        ) from e

    model = config.provider_model or "gpt-4o"
    api_key = config.api_keys.get("openai")

    provider_kwargs: dict[str, Any] = {
        "model": model,
        "api_key": api_key,
        **kwargs,
    }

    if config.provider_base_url:
        provider_kwargs["base_url"] = config.provider_base_url

    return ChatOpenAI(**provider_kwargs)


def _create_gemini_provider(config: Config, **kwargs: Any) -> BaseChatModel:
    """Create a Google Gemini provider."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as e:
        raise ProviderError(
            "langchain-google-genai is required for Gemini provider. "
            "Install with: pip install langchain-google-genai"
        ) from e

    model = config.provider_model or "gemini-pro"
    api_key = config.api_keys.get("google")

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        **kwargs,
    )


def _create_ollama_provider(config: Config, **kwargs: Any) -> BaseChatModel:
    """Create an Ollama provider."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError as e:
        raise ProviderError(
            "langchain-ollama is required for Ollama provider. "
            "Install with: pip install langchain-ollama"
        ) from e

    model = config.provider_model or "llama3.2"
    base_url = config.provider_base_url or "http://localhost:11434"

    return ChatOllama(
        model=model,
        base_url=base_url,
        **kwargs,
    )


def _create_mock_provider(config: Config, **kwargs: Any) -> BaseChatModel:
    """Create a mock provider for testing."""
    from omnia_langchain_runtime.mock_provider import MockChatModel

    return MockChatModel(
        config_path=config.mock_config_path or None,
        **kwargs,
    )
