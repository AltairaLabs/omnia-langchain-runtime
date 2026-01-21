# Type stubs for runtime_pb2
# Auto-generated protobuf types

from typing import Mapping

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class ClientMessage(_message.Message):
    session_id: str
    content: str
    metadata: Mapping[str, str]
    parts: list[ContentPart]
    def __init__(
        self,
        *,
        session_id: str = ...,
        content: str = ...,
        metadata: Mapping[str, str] | None = ...,
        parts: list[ContentPart] | None = ...,
    ) -> None: ...

class ServerMessage(_message.Message):
    chunk: Chunk
    tool_call: ToolCall
    tool_result: ToolResult
    done: Done
    error: Error
    def __init__(
        self,
        *,
        chunk: Chunk | None = ...,
        tool_call: ToolCall | None = ...,
        tool_result: ToolResult | None = ...,
        done: Done | None = ...,
        error: Error | None = ...,
    ) -> None: ...

class Chunk(_message.Message):
    content: str
    def __init__(self, *, content: str = ...) -> None: ...

class ToolCall(_message.Message):
    id: str
    name: str
    arguments_json: str
    def __init__(
        self,
        *,
        id: str = ...,
        name: str = ...,
        arguments_json: str = ...,
    ) -> None: ...

class ToolResult(_message.Message):
    id: str
    result_json: str
    is_error: bool
    def __init__(
        self,
        *,
        id: str = ...,
        result_json: str = ...,
        is_error: bool = ...,
    ) -> None: ...

class Done(_message.Message):
    final_content: str
    usage: Usage
    parts: list[ContentPart]
    def __init__(
        self,
        *,
        final_content: str = ...,
        usage: Usage | None = ...,
        parts: list[ContentPart] | None = ...,
    ) -> None: ...

class ContentPart(_message.Message):
    type: str
    text: str
    media: MediaContent
    def __init__(
        self,
        *,
        type: str = ...,
        text: str = ...,
        media: MediaContent | None = ...,
    ) -> None: ...

class MediaContent(_message.Message):
    data: str
    url: str
    mime_type: str
    def __init__(
        self,
        *,
        data: str = ...,
        url: str = ...,
        mime_type: str = ...,
    ) -> None: ...

class Usage(_message.Message):
    input_tokens: int
    output_tokens: int
    cost_usd: float
    def __init__(
        self,
        *,
        input_tokens: int = ...,
        output_tokens: int = ...,
        cost_usd: float = ...,
    ) -> None: ...

class Error(_message.Message):
    code: str
    message: str
    def __init__(self, *, code: str = ..., message: str = ...) -> None: ...

class HealthRequest(_message.Message):
    def __init__(self) -> None: ...

class HealthResponse(_message.Message):
    healthy: bool
    status: str
    def __init__(self, *, healthy: bool = ..., status: str = ...) -> None: ...
