# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Base tool adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ToolAdapterError(Exception):
    """Error during tool execution."""

    def __init__(self, message: str, tool_name: str = "", is_retryable: bool = False):
        super().__init__(message)
        self.tool_name = tool_name
        self.is_retryable = is_retryable


class ToolAdapter(ABC):
    """Abstract base class for tool adapters.

    Tool adapters handle the actual execution of tool calls by routing
    them to external services (HTTP APIs, gRPC, MCP, etc.).
    """

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Get the name of the tool this adapter handles."""

    @abstractmethod
    async def execute(self, arguments: dict[str, Any]) -> Any:
        """Execute the tool with the given arguments.

        Args:
            arguments: Tool arguments as a dictionary.

        Returns:
            Tool execution result.

        Raises:
            ToolAdapterError: If execution fails.
        """

    @abstractmethod
    async def close(self) -> None:
        """Close the adapter and release resources."""
