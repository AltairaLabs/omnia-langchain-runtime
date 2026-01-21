# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Tests for session management."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from omnia_langchain_runtime.session import InMemorySessionStore, Session


class TestSession:
    """Tests for Session class."""

    def test_create_session(self) -> None:
        """Test creating a session."""
        session = Session(session_id="test-123")
        assert session.session_id == "test-123"
        assert len(session.messages) == 0
        assert session.metadata == {}

    def test_add_message(self) -> None:
        """Test adding a message."""
        session = Session(session_id="test")
        msg = HumanMessage(content="Hello")
        session.add_message(msg)

        assert len(session.messages) == 1
        assert session.messages[0].content == "Hello"

    def test_add_messages(self) -> None:
        """Test adding multiple messages."""
        session = Session(session_id="test")
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
        ]
        session.add_messages(messages)

        assert len(session.messages) == 2

    def test_clear_messages(self) -> None:
        """Test clearing messages."""
        session = Session(session_id="test")
        session.add_message(HumanMessage(content="Test"))
        session.clear_messages()

        assert len(session.messages) == 0


class TestInMemorySessionStore:
    """Tests for InMemorySessionStore."""

    @pytest.fixture
    def store(self) -> InMemorySessionStore:
        """Create a test store."""
        return InMemorySessionStore(ttl_seconds=3600, max_sessions=100)

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, store: InMemorySessionStore) -> None:
        """Test getting a nonexistent session."""
        result = await store.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_save_and_get(self, store: InMemorySessionStore) -> None:
        """Test saving and retrieving a session."""
        session = Session(session_id="test-1")
        session.add_message(HumanMessage(content="Hello"))

        await store.save(session)
        retrieved = await store.get("test-1")

        assert retrieved is not None
        assert retrieved.session_id == "test-1"
        assert len(retrieved.messages) == 1

    @pytest.mark.asyncio
    async def test_get_or_create(self, store: InMemorySessionStore) -> None:
        """Test get_or_create."""
        # First call creates
        session1 = await store.get_or_create("new-session")
        assert session1.session_id == "new-session"

        # Second call retrieves
        session2 = await store.get_or_create("new-session")
        assert session2 is session1

    @pytest.mark.asyncio
    async def test_delete(self, store: InMemorySessionStore) -> None:
        """Test deleting a session."""
        session = Session(session_id="to-delete")
        await store.save(session)

        await store.delete("to-delete")
        result = await store.get("to-delete")

        assert result is None

    @pytest.mark.asyncio
    async def test_max_sessions_eviction(self) -> None:
        """Test LRU eviction when max sessions reached."""
        store = InMemorySessionStore(max_sessions=3)

        # Add 4 sessions
        for i in range(4):
            session = Session(session_id=f"session-{i}")
            await store.save(session)

        # First session should be evicted
        assert await store.get("session-0") is None
        assert await store.get("session-1") is not None
        assert await store.get("session-2") is not None
        assert await store.get("session-3") is not None
