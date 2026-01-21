---
title: Providers
description: LLM provider configuration for the Omnia LangChain Runtime
sidebar:
  order: 0
---

The Omnia LangChain Runtime supports multiple LLM providers.

## Supported Providers

| Provider | Type | Description |
|----------|------|-------------|
| Claude | `claude` | Anthropic's Claude models |
| OpenAI | `openai` | OpenAI GPT models |
| Gemini | `gemini` | Google's Gemini models |
| Ollama | `ollama` | Local models via Ollama |
| Mock | `mock` | Mock provider for testing |

## Configuration

Set the provider type and model via environment variables:

```bash
export OMNIA_PROVIDER_TYPE=claude
export OMNIA_PROVIDER_MODEL=claude-sonnet-4-20250514
```

## Provider-Specific Setup

Each provider requires its own API key or configuration:

### Claude

```bash
export ANTHROPIC_API_KEY=your-api-key
export OMNIA_PROVIDER_TYPE=claude
export OMNIA_PROVIDER_MODEL=claude-sonnet-4-20250514
```

### OpenAI

```bash
export OPENAI_API_KEY=your-api-key
export OMNIA_PROVIDER_TYPE=openai
export OMNIA_PROVIDER_MODEL=gpt-4
```

### Gemini

```bash
export GOOGLE_API_KEY=your-api-key
export OMNIA_PROVIDER_TYPE=gemini
export OMNIA_PROVIDER_MODEL=gemini-pro
```

### Ollama

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export OMNIA_PROVIDER_TYPE=ollama
export OMNIA_PROVIDER_MODEL=llama2
```
