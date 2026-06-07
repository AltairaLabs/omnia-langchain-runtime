# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""LangGraph agent creation utilities."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
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
) -> CompiledStateGraph:
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
    prompt_config = pack.get_prompt(prompt_name)
    if prompt_config is None:
        raise ValueError(f"Prompt '{prompt_name}' not found in pack")

    # Get system prompt from template
    template = PromptPackTemplate.from_promptpack(pack, prompt_name, model_name=model_name)

    # Apply LLM parameters
    params = template.get_parameters()
    if params:
        llm = _apply_params(llm, params)

    # Format the system prompt (with empty variables for now - will be populated at runtime)
    system_prompt = template.format()

    # Create the agent with system prompt
    # LangGraph 0.2+ uses 'prompt' parameter for system message
    agent = create_react_agent(
        llm,
        tools=list(tools),
        prompt=system_prompt,
    )

    logger.info(
        "Created agent for prompt %s with %d tools",
        prompt_name,
        len(tools),
    )

    return agent


def _apply_params(llm: BaseChatModel, params: dict[str, Any]) -> BaseChatModel:  # type: ignore[return-value]
    """Apply parameters to an LLM.

    Note: LLM parameters like temperature, max_tokens, top_p should be configured
    at provider creation time (via Provider CRD), not at runtime via bind().
    The bind() method doesn't work consistently across providers (especially Ollama).

    Args:
        llm: Language model.
        params: Parameters to apply.

    Returns:
        LLM (unchanged - params are applied at provider creation).
    """
    # Skip runtime param binding - it doesn't work reliably across providers
    # Temperature and other params should be set via Provider CRD -> providers.py
    if params:
        logger.debug(
            "Skipping runtime params (should be set at provider creation): %s", list(params.keys())
        )

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
    return int(tool_policy.max_rounds)
