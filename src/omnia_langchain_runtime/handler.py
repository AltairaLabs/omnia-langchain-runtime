# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""LangChain handler for processing conversation requests."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from promptpack import parse_promptpack

from omnia_langchain_runtime import runtime_pb2
from omnia_langchain_runtime.agent import create_agent
from omnia_langchain_runtime.config import Config, SessionType
from omnia_langchain_runtime.providers import create_provider
from omnia_langchain_runtime.session import InMemorySessionStore, SessionStore
from omnia_langchain_runtime.tools import ToolManager, load_tools_config

logger = logging.getLogger(__name__)


class LangChainHandler:
    """Handler for LangChain-based agent conversations.

    This handler manages:
    - Loading the PromptPack
    - Creating the LLM provider
    - Managing sessions
    - Executing tool calls
    - Running the agent and streaming responses
    """

    def __init__(self, config: Config):
        """Initialize the handler.

        Args:
            config: Runtime configuration.
        """
        self.config = config
        self.pack = parse_promptpack(config.promptpack_path)
        self.llm = create_provider(config)

        # Initialize session store
        self.session_store = self._create_session_store(config)

        # Initialize tool manager
        self.tool_manager: ToolManager | None = None
        if config.tools_config_path:
            tools_config = load_tools_config(config.tools_config_path)
            self.tool_manager = ToolManager(tools_config)

        logger.info(
            "Initialized LangChainHandler",
            extra={
                "pack_id": self.pack.id,
                "prompt": config.prompt_name,
                "provider": config.provider_type.value,
            },
        )

    def _create_session_store(self, config: Config) -> SessionStore:
        """Create the appropriate session store."""
        if config.session_type == SessionType.REDIS:
            from omnia_langchain_runtime.session.redis import RedisSessionStore

            return RedisSessionStore(
                url=config.session_url,
                ttl_seconds=config.session_ttl_seconds,
            )

        return InMemorySessionStore(ttl_seconds=config.session_ttl_seconds)

    async def initialize(self) -> None:
        """Initialize async resources."""
        if self.tool_manager:
            await self.tool_manager.initialize()

    async def handle_message(
        self,
        session_id: str,
        content: str | None = None,
        parts: list | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AsyncIterator[runtime_pb2.ServerMessage]:
        """Handle an incoming message and stream responses.

        Args:
            session_id: Session identifier.
            content: Text content (for text-only messages).
            parts: Content parts (for multimodal messages).
            metadata: Optional metadata.

        Yields:
            Server messages (chunks, tool calls, results, done, errors).
        """
        metadata = metadata or {}

        try:
            # Get or create session
            session = await self.session_store.get_or_create(session_id)

            # Build user message
            user_message = self._build_user_message(content, parts)
            session.add_message(user_message)

            # Get tools
            tools = []
            if self.tool_manager:
                tools = self.tool_manager.get_langchain_tools(self.pack, self.config.prompt_name)

            # Create agent
            agent = create_agent(
                self.llm,
                self.pack,
                self.config.prompt_name,
                tools,
                model_name=self.config.provider_model,
            )

            # Get variables from metadata
            variables = self._extract_variables(metadata)

            # Run agent
            final_content = ""
            total_input_tokens = 0
            total_output_tokens = 0

            async for event in agent.astream_events(
                {"messages": session.messages, "variables": variables},
                version="v2",
            ):
                event_type = event.get("event")

                if event_type == "on_chat_model_stream":
                    # Stream text chunks
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        final_content += chunk.content
                        yield runtime_pb2.ServerMessage(
                            chunk=runtime_pb2.Chunk(content=chunk.content)
                        )

                elif event_type == "on_tool_start":
                    # Tool call started
                    tool_input: dict[str, Any] = event.get("data", {}).get("input", {})
                    run_id = event.get("run_id", "")
                    tool_name = event.get("name", "")

                    yield runtime_pb2.ServerMessage(
                        tool_call=runtime_pb2.ToolCall(
                            id=run_id,
                            name=tool_name,
                            arguments_json=json.dumps(tool_input),
                        )
                    )

                elif event_type == "on_tool_end":
                    # Tool call completed
                    output = event.get("data", {}).get("output", "")
                    run_id = event.get("run_id", "")

                    # Convert output to string if needed
                    if not isinstance(output, str):
                        output = json.dumps(output)

                    yield runtime_pb2.ServerMessage(
                        tool_result=runtime_pb2.ToolResult(
                            id=run_id,
                            result_json=output,
                            is_error=False,
                        )
                    )

                elif event_type == "on_llm_end":
                    # Track token usage
                    llm_output: Any = event.get("data", {}).get("output", {})
                    if hasattr(llm_output, "llm_output") and llm_output.llm_output:
                        usage = llm_output.llm_output.get("token_usage", {})
                        total_input_tokens += usage.get("prompt_tokens", 0)
                        total_output_tokens += usage.get("completion_tokens", 0)

            # Add assistant message to session
            if final_content:
                session.add_message(AIMessage(content=final_content))

            # Save session
            await self.session_store.save(session)

            # Send done message
            yield runtime_pb2.ServerMessage(
                done=runtime_pb2.Done(
                    final_content=final_content,
                    usage=runtime_pb2.Usage(
                        input_tokens=total_input_tokens,
                        output_tokens=total_output_tokens,
                        cost_usd=0.0,  # TODO: Calculate cost
                    ),
                )
            )

        except Exception as e:
            logger.exception("Error handling message: %s", e)
            yield runtime_pb2.ServerMessage(
                error=runtime_pb2.Error(
                    code="HANDLER_ERROR",
                    message=str(e),
                )
            )

    def _build_user_message(
        self,
        content: str | None,
        parts: list | None,
    ) -> HumanMessage:
        """Build a user message from content or parts.

        Args:
            content: Text content.
            parts: Multimodal content parts.

        Returns:
            HumanMessage.
        """
        if parts:
            # Convert protobuf parts to LangChain format
            lc_parts = []
            for part in parts:
                if part.type == "text":
                    lc_parts.append({"type": "text", "text": part.text})
                elif part.type == "image" and part.media:
                    if part.media.url:
                        lc_parts.append(
                            {
                                "type": "image_url",
                                "image_url": {"url": part.media.url},
                            }
                        )
                    elif part.media.data:
                        data_url = f"data:{part.media.mime_type};base64,{part.media.data}"
                        lc_parts.append(
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url},
                            }
                        )

            return HumanMessage(content=lc_parts)  # type: ignore[arg-type]

        return HumanMessage(content=content or "")

    def _extract_variables(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Extract prompt variables from metadata.

        Args:
            metadata: Request metadata.

        Returns:
            Variables dictionary.
        """
        # Variables can be passed as a JSON string in metadata
        variables_str = metadata.get("variables")
        if variables_str:
            try:
                result: dict[str, Any] = json.loads(variables_str)
                return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse variables from metadata")

        return {}

    async def health_check(self) -> bool:
        """Check if the handler is healthy.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            # Check if pack is loaded
            if self.pack is None:
                return False

            # Check if prompt exists
            prompt = self.pack.get_prompt(self.config.prompt_name)
            if prompt is None:
                return False

            return True
        except Exception as e:
            logger.warning("Health check failed: %s", e)
            return False

    async def close(self) -> None:
        """Close the handler and release resources."""
        await self.session_store.close()
        if self.tool_manager:
            await self.tool_manager.close()
