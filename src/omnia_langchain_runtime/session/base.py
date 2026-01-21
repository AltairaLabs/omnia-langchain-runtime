# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Base session interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from langchain_core.messages import BaseMessage


@dataclass
class Session:
    """A conversation session containing message history."""

    session_id: str
    messages: list[BaseMessage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the session.

        Args:
            message: The message to add.
        """
        self.messages.append(message)
        self.updated_at = datetime.utcnow()

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add multiple messages to the session.

        Args:
            messages: The messages to add.
        """
        self.messages.extend(messages)
        self.updated_at = datetime.utcnow()

    def clear_messages(self) -> None:
        """Clear all messages from the session."""
        self.messages = []
        self.updated_at = datetime.utcnow()


class SessionStore(ABC):
    """Abstract base class for session storage."""

    @abstractmethod
    async def get(self, session_id: str) -> Session | None:
        """Get a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            The session if found, None otherwise.
        """

    @abstractmethod
    async def save(self, session: Session) -> None:
        """Save a session.

        Args:
            session: The session to save.
        """

    @abstractmethod
    async def delete(self, session_id: str) -> None:
        """Delete a session.

        Args:
            session_id: The session identifier.
        """

    async def get_or_create(self, session_id: str) -> Session:
        """Get an existing session or create a new one.

        Args:
            session_id: The session identifier.

        Returns:
            The existing or new session.
        """
        session = await self.get(session_id)
        if session is None:
            session = Session(session_id=session_id)
            await self.save(session)
        return session

    @abstractmethod
    async def close(self) -> None:
        """Close the session store and release resources."""
