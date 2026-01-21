# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""LangGraph agent creation utilities."""

from __future__ import annotations

import logging
from typing import Any, Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from langgraph.graph.graph import CompiledGraph

from promptpack import PromptPack, ToolPolicy
from promptpack_langchain import PromptPackTemplate

logger = logging.getLogger(__name__)


def create_agent(
    llm: BaseChatModel,
    pack: PromptPack,
    prompt_name: str,
    tools: Sequence[BaseTool],
    *,
    model_name: str | None = None,
) -> CompiledGraph:
    """Create a LangGraph ReAct agent from a PromptPack.

    Args:
        llm: Language model to use.
        pack: PromptPack containing the prompt configuration.
        prompt_name: Name of the prompt to use.
        tools: List of tools available to the agent.
        model_name: Optional model name for overrides.

    Returns:
        Compiled LangGraph agent.
    """
    prompt = pack.get_prompt(prompt_name)
    if prompt is None:
        raise ValueError(f"Prompt '{prompt_name}' not found in pack")

    # Get system prompt
    template = PromptPackTemplate.from_promptpack(pack, prompt_name, model_name=model_name)

    # Apply LLM parameters
    params = template.get_parameters()
    if params:
        llm = _apply_params(llm, params)

    # Get tool policy
    tool_policy = prompt.tool_policy

    # Create the agent
    agent = create_react_agent(
        llm,
        tools=list(tools),
        state_modifier=_create_state_modifier(template),
    )

    logger.info(
        "Created agent for prompt %s with %d tools",
        prompt_name,
        len(tools),
    )

    return agent


def _apply_params(llm: BaseChatModel, params: dict[str, Any]) -> BaseChatModel:
    """Apply parameters to an LLM.

    Args:
        llm: Language model.
        params: Parameters to apply.

    Returns:
        LLM with parameters applied.
    """
    # Most LangChain models support bind() for runtime config
    bind_params = {}

    if "temperature" in params:
        bind_params["temperature"] = params["temperature"]
    if "max_tokens" in params:
        bind_params["max_tokens"] = params["max_tokens"]
    if "top_p" in params:
        bind_params["top_p"] = params["top_p"]

    if bind_params:
        try:
            return llm.bind(**bind_params)
        except Exception as e:
            logger.warning("Failed to bind params to LLM: %s", e)

    return llm


def _create_state_modifier(template: PromptPackTemplate):
    """Create a state modifier that adds the system prompt.

    Args:
        template: PromptPack template.

    Returns:
        State modifier function.
    """

    def modifier(state: dict[str, Any]) -> list[BaseMessage]:
        """Add system message to the state."""
        from langchain_core.messages import SystemMessage

        messages = state.get("messages", [])

        # Get variables from state metadata if available
        variables = state.get("variables", {})

        # Format the system prompt
        system_content = template.format(**variables)

        # Prepend system message if not already present
        if messages and not isinstance(messages[0], SystemMessage):
            return [SystemMessage(content=system_content)] + list(messages)

        return list(messages)

    return modifier


def get_max_iterations(tool_policy: ToolPolicy | None) -> int:
    """Get the maximum iterations from tool policy.

    Args:
        tool_policy: Tool policy configuration.

    Returns:
        Maximum number of iterations.
    """
    if tool_policy is None:
        return 5  # Default
    return tool_policy.max_rounds
