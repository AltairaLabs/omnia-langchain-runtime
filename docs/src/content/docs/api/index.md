---
title: API Reference
description: API reference for the Omnia LangChain Runtime
sidebar:
  order: 0
---

This section contains the API reference documentation for the Omnia LangChain Runtime.

## Python API

### Runtime Server

```python
from omnia_langchain_runtime import RuntimeServer

server = RuntimeServer()
server.start()
```

### Providers

```python
from omnia_langchain_runtime.providers import create_provider

provider = create_provider(
    provider_type="claude",
    model="claude-sonnet-4-20250514"
)
```

### Session Stores

```python
from omnia_langchain_runtime.session import create_session_store

# Memory store
store = create_session_store(session_type="memory")

# Redis store
store = create_session_store(
    session_type="redis",
    url="redis://localhost:6379"
)
```

### Tools

```python
from omnia_langchain_runtime.tools import load_tools

tools = load_tools("/path/to/tools.yaml")
```

## gRPC API

See the [gRPC Protocol](/grpc/) section for the full protocol definition.

## Environment Variables

See the [Configuration](/getting-started/configuration/) guide for all supported environment variables.
