# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""HTTP tool adapter for calling external HTTP APIs."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from omnia_langchain_runtime.tools.adapter import ToolAdapter, ToolAdapterError
from omnia_langchain_runtime.tools.config import HandlerConfig

logger = logging.getLogger(__name__)


class HTTPToolAdapter(ToolAdapter):
    """Tool adapter for HTTP API calls."""

    def __init__(
        self,
        handler: HandlerConfig,
        client: httpx.AsyncClient | None = None,
    ):
        """Initialize the HTTP adapter.

        Args:
            handler: Handler configuration.
            client: Optional httpx client to use.
        """
        self.handler = handler
        self._client = client
        self._owns_client = client is None

        # Get HTTP-specific config or use defaults
        self.http_config = handler.http_config
        if self.http_config:
            self.endpoint = self.http_config.endpoint
            self.method = self.http_config.method
            self.headers = self.http_config.headers
            self.content_type = self.http_config.content_type
        else:
            self.endpoint = handler.endpoint
            self.method = "POST"
            self.headers = {}
            self.content_type = "application/json"

        # Parse timeout
        self.timeout = self._parse_timeout(handler.timeout)

    @property
    def tool_name(self) -> str:
        """Get the tool name."""
        if self.handler.tool:
            return self.handler.tool.name
        return self.handler.name

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def execute(self, arguments: dict[str, Any]) -> Any:
        """Execute the HTTP tool call.

        Args:
            arguments: Tool arguments.

        Returns:
            Response data.

        Raises:
            ToolAdapterError: If the request fails.
        """
        client = await self._get_client()

        headers = dict(self.headers)
        headers["Content-Type"] = self.content_type

        try:
            logger.debug(
                "Executing HTTP tool %s: %s %s",
                self.tool_name,
                self.method,
                self.endpoint,
            )

            response = await client.request(
                method=self.method,
                url=self.endpoint,
                headers=headers,
                json=arguments,
            )

            response.raise_for_status()

            # Try to parse as JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text

        except httpx.TimeoutException as e:
            raise ToolAdapterError(
                f"Request timed out: {e}",
                tool_name=self.tool_name,
                is_retryable=True,
            ) from e
        except httpx.HTTPStatusError as e:
            is_retryable = e.response.status_code >= 500
            raise ToolAdapterError(
                f"HTTP error {e.response.status_code}: {e.response.text}",
                tool_name=self.tool_name,
                is_retryable=is_retryable,
            ) from e
        except httpx.RequestError as e:
            raise ToolAdapterError(
                f"Request failed: {e}",
                tool_name=self.tool_name,
                is_retryable=True,
            ) from e

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and self._owns_client:
            await self._client.aclose()
            self._client = None

    def _parse_timeout(self, timeout_str: str) -> float:
        """Parse timeout string to seconds.

        Args:
            timeout_str: Timeout string (e.g., "30s", "1m").

        Returns:
            Timeout in seconds.
        """
        if timeout_str.endswith("s"):
            return float(timeout_str[:-1])
        if timeout_str.endswith("m"):
            return float(timeout_str[:-1]) * 60
        if timeout_str.endswith("h"):
            return float(timeout_str[:-1]) * 3600
        try:
            return float(timeout_str)
        except ValueError:
            return 30.0  # Default
