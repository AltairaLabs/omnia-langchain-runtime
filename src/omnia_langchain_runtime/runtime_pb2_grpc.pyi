# Type stubs for runtime_pb2_grpc
# Auto-generated gRPC types

from collections.abc import AsyncIterator, Iterator

import grpc
from grpc import aio

from . import runtime_pb2

class RuntimeServiceStub:
    def __init__(self, channel: grpc.Channel) -> None: ...
    def Converse(
        self,
        request_iterator: Iterator[runtime_pb2.ClientMessage],
        **kwargs,
    ) -> Iterator[runtime_pb2.ServerMessage]: ...
    def Health(
        self,
        request: runtime_pb2.HealthRequest,
        **kwargs,
    ) -> runtime_pb2.HealthResponse: ...

class RuntimeServiceServicer:
    def Converse(
        self,
        request_iterator: AsyncIterator[runtime_pb2.ClientMessage],
        context: aio.ServicerContext,
    ) -> AsyncIterator[runtime_pb2.ServerMessage]: ...
    async def Health(
        self,
        request: runtime_pb2.HealthRequest,
        context: aio.ServicerContext,
    ) -> runtime_pb2.HealthResponse: ...

def add_RuntimeServiceServicer_to_server(
    servicer: RuntimeServiceServicer,
    server: grpc.Server | aio.Server,
) -> None: ...
