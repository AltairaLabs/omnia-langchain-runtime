# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""gRPC server implementation for the LangChain runtime."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from concurrent import futures
from typing import TYPE_CHECKING

import grpc
from grpc import aio

from omnia_langchain_runtime import runtime_pb2, runtime_pb2_grpc
from omnia_langchain_runtime.config import Config

if TYPE_CHECKING:
    from omnia_langchain_runtime.handler import LangChainHandler

logger = logging.getLogger(__name__)


class RuntimeServicer(runtime_pb2_grpc.RuntimeServiceServicer):
    """gRPC servicer implementing the RuntimeService protocol."""

    def __init__(self, handler: LangChainHandler):
        """Initialize the servicer.

        Args:
            handler: The LangChainHandler that processes requests.
        """
        self.handler = handler

    async def Converse(
        self,
        request_iterator: AsyncIterator[runtime_pb2.ClientMessage],
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[runtime_pb2.ServerMessage]:
        """Handle bidirectional streaming conversation.

        Args:
            request_iterator: Stream of client messages.
            context: gRPC context.

        Yields:
            Server messages (chunks, tool calls, results, done, errors).
        """
        try:
            async for client_msg in request_iterator:
                session_id = client_msg.session_id
                metadata = dict(client_msg.metadata)

                # Get content from parts or legacy content field
                if client_msg.parts:
                    content_parts = list(client_msg.parts)
                else:
                    content_parts = None
                    content = client_msg.content

                logger.info(
                    "Received message",
                    extra={"session_id": session_id, "has_parts": bool(content_parts)},
                )

                # Process through handler
                async for response in self.handler.handle_message(
                    session_id=session_id,
                    content=content if not content_parts else None,
                    parts=content_parts,
                    metadata=metadata,
                ):
                    yield response

        except asyncio.CancelledError:
            logger.info("Conversation cancelled by client")
            raise
        except Exception as e:
            logger.exception("Error in conversation: %s", e)
            yield runtime_pb2.ServerMessage(
                error=runtime_pb2.Error(
                    code="INTERNAL_ERROR",
                    message=str(e),
                )
            )

    async def Health(
        self,
        request: runtime_pb2.HealthRequest,
        context: grpc.aio.ServicerContext,
    ) -> runtime_pb2.HealthResponse:
        """Check runtime health.

        Args:
            request: Health check request.
            context: gRPC context.

        Returns:
            Health response indicating readiness.
        """
        try:
            is_healthy = await self.handler.health_check()
            return runtime_pb2.HealthResponse(
                healthy=is_healthy,
                status="ready" if is_healthy else "not ready",
            )
        except Exception as e:
            logger.exception("Health check failed: %s", e)
            return runtime_pb2.HealthResponse(
                healthy=False,
                status=f"error: {e}",
            )


async def serve(handler: LangChainHandler, config: Config) -> None:
    """Start the gRPC server.

    Args:
        handler: The LangChainHandler to process requests.
        config: Runtime configuration.
    """
    server = aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_send_message_length", 50 * 1024 * 1024),  # 50MB
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),  # 50MB
        ],
    )

    runtime_pb2_grpc.add_RuntimeServiceServicer_to_server(
        RuntimeServicer(handler),
        server,
    )

    listen_addr = f"[::]:{config.grpc_port}"
    server.add_insecure_port(listen_addr)

    logger.info("Starting gRPC server on %s", listen_addr)

    await server.start()

    # Start health server in background
    health_task = asyncio.create_task(
        _run_health_server(handler, config.health_port)
    )

    try:
        await server.wait_for_termination()
    finally:
        health_task.cancel()
        try:
            await health_task
        except asyncio.CancelledError:
            pass


async def _run_health_server(handler: LangChainHandler, port: int) -> None:
    """Run HTTP health check server.

    Args:
        handler: The handler to check health.
        port: Port to listen on.
    """
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path == "/healthz" or self.path == "/readyz":
                # Simple synchronous health check
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"ok")
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format: str, *args) -> None:
            # Suppress request logging
            pass

    server = HTTPServer(("", port), HealthHandler)
    logger.info("Starting health server on port %d", port)

    # Run in thread to not block async loop
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        # Keep running until cancelled
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        server.shutdown()
        raise
