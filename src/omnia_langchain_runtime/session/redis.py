# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Redis session store."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from omnia_langchain_runtime.session.base import Session, SessionStore

try:
    import redis.asyncio as redis
except ImportError as e:
    raise ImportError(
        "Redis support requires the 'redis' package. "
        "Install with: pip install omnia-langchain-runtime[redis]"
    ) from e

logger = logging.getLogger(__name__)


class RedisSessionStore(SessionStore):
    """Redis-backed session store.

    Stores sessions in Redis with automatic TTL expiration.
    """

    def __init__(
        self,
        url: str,
        ttl_seconds: int = 86400,
        key_prefix: str = "omnia:session:",
    ):
        """Initialize the Redis store.

        Args:
            url: Redis connection URL (e.g., redis://localhost:6379).
            ttl_seconds: Time-to-live for sessions in seconds.
            key_prefix: Prefix for Redis keys.
        """
        self.url = url
        self.ttl_seconds = ttl_seconds
        self.key_prefix = key_prefix
        self._client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis:
        """Get or create the Redis client."""
        if self._client is None:
            self._client = redis.from_url(self.url, decode_responses=True)
        return self._client

    def _key(self, session_id: str) -> str:
        """Get the Redis key for a session ID."""
        return f"{self.key_prefix}{session_id}"

    async def get(self, session_id: str) -> Session | None:
        """Get a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            The session if found, None otherwise.
        """
        client = await self._get_client()
        data = await client.get(self._key(session_id))

        if data is None:
            return None

        try:
            return self._deserialize(session_id, data)
        except Exception as e:
            logger.warning("Failed to deserialize session %s: %s", session_id, e)
            return None

    async def save(self, session: Session) -> None:
        """Save a session.

        Args:
            session: The session to save.
        """
        client = await self._get_client()
        session.updated_at = datetime.utcnow()

        data = self._serialize(session)
        await client.setex(
            self._key(session.session_id),
            self.ttl_seconds,
            data,
        )

    async def delete(self, session_id: str) -> None:
        """Delete a session.

        Args:
            session_id: The session identifier.
        """
        client = await self._get_client()
        await client.delete(self._key(session_id))

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    def _serialize(self, session: Session) -> str:
        """Serialize a session to JSON.

        Args:
            session: The session to serialize.

        Returns:
            JSON string representation.
        """
        messages_data = []
        for msg in session.messages:
            msg_data = {
                "type": msg.__class__.__name__,
                "content": msg.content,
            }
            if hasattr(msg, "additional_kwargs"):
                msg_data["additional_kwargs"] = msg.additional_kwargs
            if isinstance(msg, ToolMessage):
                msg_data["tool_call_id"] = msg.tool_call_id
            messages_data.append(msg_data)

        return json.dumps({
            "messages": messages_data,
            "metadata": session.metadata,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
        })

    def _deserialize(self, session_id: str, data: str) -> Session:
        """Deserialize a session from JSON.

        Args:
            session_id: The session identifier.
            data: JSON string representation.

        Returns:
            Deserialized session.
        """
        parsed = json.loads(data)

        messages: list[BaseMessage] = []
        for msg_data in parsed.get("messages", []):
            msg_type = msg_data.get("type", "HumanMessage")
            content = msg_data.get("content", "")
            additional_kwargs = msg_data.get("additional_kwargs", {})

            if msg_type == "HumanMessage":
                messages.append(HumanMessage(content=content, additional_kwargs=additional_kwargs))
            elif msg_type == "AIMessage":
                messages.append(AIMessage(content=content, additional_kwargs=additional_kwargs))
            elif msg_type == "SystemMessage":
                messages.append(SystemMessage(content=content, additional_kwargs=additional_kwargs))
            elif msg_type == "ToolMessage":
                messages.append(
                    ToolMessage(
                        content=content,
                        tool_call_id=msg_data.get("tool_call_id", ""),
                        additional_kwargs=additional_kwargs,
                    )
                )
            else:
                # Default to human message
                messages.append(HumanMessage(content=content))

        return Session(
            session_id=session_id,
            messages=messages,
            metadata=parsed.get("metadata", {}),
            created_at=datetime.fromisoformat(parsed["created_at"]),
            updated_at=datetime.fromisoformat(parsed["updated_at"]),
        )
