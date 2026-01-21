---
title: gRPC Protocol
description: The Omnia runtime gRPC protocol implementation
sidebar:
  order: 0
---

The Omnia LangChain Runtime implements the `omnia.runtime.v1.RuntimeService` gRPC protocol.

## Protocol Overview

The runtime communicates with the Omnia facade via gRPC, enabling:

- Streaming conversations
- Session management
- Tool execution
- Health checks

## Service Definition

```protobuf
service RuntimeService {
  rpc Chat(stream ChatRequest) returns (stream ChatResponse);
  rpc Health(HealthRequest) returns (HealthResponse);
}
```

## Message Types

### ChatRequest

```protobuf
message ChatRequest {
  string session_id = 1;
  string message = 2;
  map<string, string> metadata = 3;
}
```

### ChatResponse

```protobuf
message ChatResponse {
  string session_id = 1;
  string content = 2;
  bool done = 3;
  repeated ToolCall tool_calls = 4;
}
```

## Streaming

The runtime supports bidirectional streaming for real-time conversations:

1. Client sends `ChatRequest` messages
2. Server streams `ChatResponse` messages
3. Tool calls are handled within the stream
4. `done=true` indicates completion

## Health Checks

The health endpoint runs on a separate port (default: 9001) for Kubernetes probes:

```bash
grpcurl -plaintext localhost:9001 grpc.health.v1.Health/Check
```
