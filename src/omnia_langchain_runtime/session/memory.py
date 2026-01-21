# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""In-memory session store."""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from datetime import datetime, timedelta

from omnia_langchain_runtime.session.base import Session, SessionStore


class InMemorySessionStore(SessionStore):
    """In-memory session store with TTL support.

    Sessions are stored in memory and automatically expire after the TTL.
    Uses an OrderedDict for LRU-style cleanup when max_sessions is reached.
    """

    def __init__(
        self,
        ttl_seconds: int = 86400,
        max_sessions: int = 10000,
    ):
        """Initialize the in-memory store.

        Args:
            ttl_seconds: Time-to-live for sessions in seconds (default 24h).
            max_sessions: Maximum number of sessions to store.
        """
        self.ttl = timedelta(seconds=ttl_seconds)
        self.max_sessions = max_sessions
        self._sessions: OrderedDict[str, Session] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, session_id: str) -> Session | None:
        """Get a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            The session if found and not expired, None otherwise.
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None

            # Check if expired
            if datetime.utcnow() - session.updated_at > self.ttl:
                del self._sessions[session_id]
                return None

            # Move to end (most recently accessed)
            self._sessions.move_to_end(session_id)
            return session

    async def save(self, session: Session) -> None:
        """Save a session.

        Args:
            session: The session to save.
        """
        async with self._lock:
            # Update timestamp
            session.updated_at = datetime.utcnow()

            # Remove if exists to update position
            if session.session_id in self._sessions:
                del self._sessions[session.session_id]

            # Evict oldest if at capacity
            while len(self._sessions) >= self.max_sessions:
                self._sessions.popitem(last=False)

            # Add to end
            self._sessions[session.session_id] = session

    async def delete(self, session_id: str) -> None:
        """Delete a session.

        Args:
            session_id: The session identifier.
        """
        async with self._lock:
            self._sessions.pop(session_id, None)

    async def close(self) -> None:
        """Close the store (no-op for memory store)."""
        pass

    async def cleanup_expired(self) -> int:
        """Remove expired sessions.

        Returns:
            Number of sessions removed.
        """
        async with self._lock:
            now = datetime.utcnow()
            expired = [
                sid
                for sid, session in self._sessions.items()
                if now - session.updated_at > self.ttl
            ]
            for sid in expired:
                del self._sessions[sid]
            return len(expired)

    @property
    def size(self) -> int:
        """Get the number of sessions stored."""
        return len(self._sessions)
