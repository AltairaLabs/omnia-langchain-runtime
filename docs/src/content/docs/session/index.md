---
title: Session Management
description: Configure session storage for conversation persistence
sidebar:
  order: 0
---

The Omnia LangChain Runtime supports multiple session storage backends for maintaining conversation history.

## Session Types

| Type | Description | Use Case |
|------|-------------|----------|
| `memory` | In-memory storage | Development, single instance |
| `redis` | Redis-backed storage | Production, distributed |

## Memory Sessions

The default session type stores conversations in memory:

```bash
export OMNIA_SESSION_TYPE=memory
```

Memory sessions are lost when the runtime restarts.

## Redis Sessions

For production deployments, use Redis for persistent session storage:

```bash
export OMNIA_SESSION_TYPE=redis
export OMNIA_SESSION_URL=redis://localhost:6379
```

### Redis Installation

Install with Redis support:

```bash
pip install omnia-langchain-runtime[redis]
```

### Redis URL Format

```
redis://[[username:]password@]host[:port][/database]
```

Examples:
- `redis://localhost:6379`
- `redis://user:password@redis.example.com:6379/0`

## Session Lifecycle

1. Sessions are created when a new conversation starts
2. Messages are stored with each interaction
3. Sessions persist across requests (with Redis)
4. Sessions can be explicitly cleared via the gRPC API
