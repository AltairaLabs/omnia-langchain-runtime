# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Mock LLM provider for testing."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterator, List

import yaml
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

logger = logging.getLogger(__name__)


class MockChatModel(BaseChatModel):
    """Mock chat model for testing.

    Returns predefined responses based on configuration or simple echo behavior.
    """

    responses: list[dict[str, Any]] = []
    response_index: int = 0
    default_response: str = "This is a mock response."

    def __init__(
        self,
        config_path: str | None = None,
        responses: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ):
        """Initialize the mock model.

        Args:
            config_path: Path to YAML file with mock responses.
            responses: List of response configurations.
            **kwargs: Additional arguments.
        """
        super().__init__(**kwargs)

        if config_path:
            self.responses = self._load_config(config_path)
        elif responses:
            self.responses = responses
        else:
            self.responses = []

        self.response_index = 0

    def _load_config(self, path: str) -> list[dict[str, Any]]:
        """Load mock responses from a YAML file."""
        file_path = Path(path)
        if not file_path.exists():
            logger.warning("Mock config not found: %s", path)
            return []

        with open(file_path) as f:
            data = yaml.safe_load(f) or {}

        return data.get("responses", [])

    @property
    def _llm_type(self) -> str:
        """Return the LLM type."""
        return "mock"

    @property
    def _identifying_params(self) -> dict[str, Any]:
        """Return identifying parameters."""
        return {"responses": len(self.responses)}

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response.

        Args:
            messages: Input messages.
            stop: Stop sequences.
            run_manager: Callback manager.
            **kwargs: Additional arguments.

        Returns:
            Chat result with mock response.
        """
        # Get the last user message content
        last_message = messages[-1] if messages else None
        user_content = ""
        if last_message:
            if isinstance(last_message.content, str):
                user_content = last_message.content
            elif isinstance(last_message.content, list):
                # Multimodal content
                for part in last_message.content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        user_content = part.get("text", "")
                        break

        # Find matching response or use default
        response_content = self._get_response(user_content)

        # Check if response includes tool calls
        tool_calls = []
        if isinstance(response_content, dict):
            if "tool_calls" in response_content:
                tool_calls = response_content["tool_calls"]
                response_content = response_content.get("content", "")

        message = AIMessage(
            content=response_content if isinstance(response_content, str) else "",
            tool_calls=tool_calls,
        )

        return ChatResult(
            generations=[
                ChatGeneration(
                    message=message,
                )
            ],
            llm_output={
                "token_usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30,
                }
            },
        )

    def _get_response(self, user_content: str) -> str | dict[str, Any]:
        """Get the appropriate response for input.

        Args:
            user_content: User message content.

        Returns:
            Response content (string or dict with tool_calls).
        """
        # Check for pattern matches in configured responses
        for response_config in self.responses:
            pattern = response_config.get("match")
            if pattern and pattern.lower() in user_content.lower():
                return response_config.get("response", self.default_response)

        # Use sequential responses if available
        if self.responses:
            response = self.responses[self.response_index % len(self.responses)]
            self.response_index += 1
            return response.get("response", self.default_response)

        # Default echo behavior
        return f"Mock response to: {user_content[:100]}"

    def bind_tools(self, tools: list[Any], **kwargs: Any) -> "MockChatModel":
        """Bind tools to the model (no-op for mock)."""
        return self
