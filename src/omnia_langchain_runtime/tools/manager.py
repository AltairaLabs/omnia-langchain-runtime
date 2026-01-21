# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Tool manager for routing tool calls to appropriate adapters."""

from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.tools import StructuredTool
from promptpack import PromptPack

from omnia_langchain_runtime.tools.adapter import ToolAdapter, ToolAdapterError
from omnia_langchain_runtime.tools.config import HandlerConfig, ToolsConfig
from omnia_langchain_runtime.tools.http import HTTPToolAdapter

logger = logging.getLogger(__name__)


class ToolManager:
    """Manages tool adapters and routes tool calls."""

    def __init__(self, tools_config: ToolsConfig | None = None):
        """Initialize the tool manager.

        Args:
            tools_config: Tools configuration from tools.yaml.
        """
        self.tools_config = tools_config
        self._adapters: dict[str, ToolAdapter] = {}

    async def initialize(self) -> None:
        """Initialize all tool adapters."""
        if self.tools_config is None:
            return

        for handler in self.tools_config.handlers:
            adapter = self._create_adapter(handler)
            if adapter:
                self._adapters[adapter.tool_name] = adapter
                logger.info("Initialized adapter for tool: %s", adapter.tool_name)

    def _create_adapter(self, handler: HandlerConfig) -> ToolAdapter | None:
        """Create an adapter for a handler.

        Args:
            handler: Handler configuration.

        Returns:
            Tool adapter or None if type is not supported.
        """
        if handler.type == "http":
            return HTTPToolAdapter(handler)

        # Add other adapter types here (gRPC, MCP, OpenAPI)
        logger.warning("Unsupported handler type: %s", handler.type)
        return None

    async def execute(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool call.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.

        Returns:
            Tool execution result.

        Raises:
            ToolAdapterError: If tool not found or execution fails.
        """
        adapter = self._adapters.get(tool_name)
        if adapter is None:
            raise ToolAdapterError(
                f"No adapter found for tool: {tool_name}",
                tool_name=tool_name,
            )

        # Retry logic
        handler = self.tools_config.get_tool_handler(tool_name) if self.tools_config else None
        max_retries = handler.retries if handler else 0

        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                return await adapter.execute(arguments)
            except ToolAdapterError as e:
                last_error = e
                if not e.is_retryable or attempt >= max_retries:
                    raise
                logger.warning(
                    "Tool %s failed (attempt %d/%d): %s",
                    tool_name,
                    attempt + 1,
                    max_retries + 1,
                    e,
                )

        raise last_error or ToolAdapterError("Unknown error", tool_name=tool_name)

    def get_langchain_tools(
        self,
        pack: PromptPack,
        prompt_name: str,
    ) -> list[StructuredTool]:
        """Get LangChain tools for a prompt.

        Creates StructuredTools that route to the appropriate adapters.

        Args:
            pack: PromptPack containing tool definitions.
            prompt_name: Name of the prompt to get tools for.

        Returns:
            List of LangChain StructuredTools.
        """
        from promptpack_langchain import convert_tools

        # Create handler functions that route to adapters
        handlers = {}
        for tool in pack.get_tools_for_prompt(prompt_name):
            handlers[tool.name] = self._create_tool_handler(tool.name)

        return convert_tools(pack, prompt_name, handlers=handlers)

    def _create_tool_handler(self, tool_name: str):
        """Create a sync handler function for a tool.

        Args:
            tool_name: Name of the tool.

        Returns:
            Handler function.
        """

        def handler(**kwargs) -> str:
            # This will be called from LangChain sync context
            # We need to run the async execute in the event loop
            import asyncio

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create a new loop in a thread
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(
                            asyncio.run, self.execute(tool_name, kwargs)
                        )
                        result = future.result()
                else:
                    result = loop.run_until_complete(self.execute(tool_name, kwargs))

                # Convert result to string for LangChain
                if isinstance(result, str):
                    return result
                return json.dumps(result)

            except ToolAdapterError as e:
                return json.dumps({"error": str(e), "tool": tool_name})
            except Exception as e:
                logger.exception("Tool %s failed: %s", tool_name, e)
                return json.dumps({"error": str(e), "tool": tool_name})

        return handler

    async def close(self) -> None:
        """Close all adapters."""
        for adapter in self._adapters.values():
            await adapter.close()
        self._adapters.clear()
