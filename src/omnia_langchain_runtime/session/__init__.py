# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Session management for conversation history."""

from omnia_langchain_runtime.session.base import Session, SessionStore
from omnia_langchain_runtime.session.memory import InMemorySessionStore

__all__ = [
    "Session",
    "SessionStore",
    "InMemorySessionStore",
]

# Conditional import for Redis
try:
    from omnia_langchain_runtime.session.redis import RedisSessionStore

    __all__.append("RedisSessionStore")
except ImportError:
    # Redis not installed
    pass
