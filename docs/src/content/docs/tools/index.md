---
title: Tools
description: Extending agent capabilities with tools
sidebar:
  order: 0
---

The Omnia LangChain Runtime supports extending agent capabilities through tools.

## Tool Types

| Type | Description |
|------|-------------|
| HTTP | RESTful API tools |
| MCP | Model Context Protocol tools |

## Configuration

Tools are configured via a YAML file:

```bash
export OMNIA_TOOLS_CONFIG=/etc/omnia/tools/tools.yaml
```

## HTTP Tools

HTTP tools allow agents to call external APIs:

```yaml
tools:
  - name: weather
    type: http
    description: Get current weather for a location
    endpoint: https://api.weather.example.com/current
    method: GET
    parameters:
      - name: location
        type: string
        required: true
        description: City name or coordinates
```

## MCP Tools

MCP (Model Context Protocol) tools integrate with MCP servers:

```yaml
tools:
  - name: database
    type: mcp
    server: mcp://localhost:3000
    capabilities:
      - query
      - insert
```

## Tool Adapters

The runtime includes adapters for converting tool configurations to LangChain tools:

- `HTTPToolAdapter`: Converts HTTP tool configs to LangChain tools
- `MCPToolAdapter`: Integrates MCP server tools

## Custom Tools

For custom tool implementations, extend the base adapter class and register with the runtime.
