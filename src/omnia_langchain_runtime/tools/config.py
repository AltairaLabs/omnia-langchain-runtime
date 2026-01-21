# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Tools configuration parsing from YAML."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml


@dataclass
class ToolDefinition:
    """Tool interface definition."""

    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None


@dataclass
class HTTPConfig:
    """HTTP handler configuration."""

    endpoint: str
    method: str = "POST"
    headers: dict[str, str] = field(default_factory=dict)
    content_type: str = "application/json"


@dataclass
class GRPCConfig:
    """gRPC handler configuration."""

    endpoint: str
    tls: bool = False
    tls_cert_path: str | None = None
    tls_key_path: str | None = None
    tls_ca_path: str | None = None
    tls_insecure_skip_verify: bool = False


@dataclass
class MCPConfig:
    """MCP handler configuration."""

    transport: Literal["stdio", "sse"]
    endpoint: str | None = None
    command: str | None = None
    args: list[str] = field(default_factory=list)
    work_dir: str | None = None
    env: dict[str, str] = field(default_factory=dict)


@dataclass
class OpenAPIConfig:
    """OpenAPI handler configuration."""

    spec_url: str
    base_url: str | None = None
    operation_filter: list[str] = field(default_factory=list)


@dataclass
class HandlerConfig:
    """Configuration for a single tool handler."""

    name: str
    type: Literal["http", "grpc", "mcp", "openapi"]
    endpoint: str
    tool: ToolDefinition | None = None
    http_config: HTTPConfig | None = None
    grpc_config: GRPCConfig | None = None
    mcp_config: MCPConfig | None = None
    openapi_config: OpenAPIConfig | None = None
    timeout: str = "30s"
    retries: int = 0


@dataclass
class ToolsConfig:
    """Complete tools configuration."""

    handlers: list[HandlerConfig] = field(default_factory=list)

    def get_handler(self, name: str) -> HandlerConfig | None:
        """Get a handler by name."""
        for handler in self.handlers:
            if handler.name == name:
                return handler
        return None

    def get_tool_handler(self, tool_name: str) -> HandlerConfig | None:
        """Get a handler by its tool name."""
        for handler in self.handlers:
            if handler.tool and handler.tool.name == tool_name:
                return handler
        return None


def load_tools_config(path: str | Path) -> ToolsConfig:
    """Load tools configuration from a YAML file.

    Args:
        path: Path to the tools.yaml file.

    Returns:
        Parsed ToolsConfig.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the YAML is invalid.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Tools config not found: {path}")

    with open(file_path) as f:
        data = yaml.safe_load(f) or {}

    return _parse_config(data)


def _parse_config(data: dict[str, Any]) -> ToolsConfig:
    """Parse tools configuration from dict."""
    handlers = []

    for handler_data in data.get("handlers", []):
        handler = _parse_handler(handler_data)
        handlers.append(handler)

    return ToolsConfig(handlers=handlers)


def _parse_handler(data: dict[str, Any]) -> HandlerConfig:
    """Parse a single handler configuration."""
    handler_type = data.get("type", "http")

    handler = HandlerConfig(
        name=data["name"],
        type=handler_type,
        endpoint=data.get("endpoint", ""),
        timeout=data.get("timeout", "30s"),
        retries=data.get("retries", 0),
    )

    # Parse tool definition
    if "tool" in data:
        tool_data = data["tool"]
        handler.tool = ToolDefinition(
            name=tool_data["name"],
            description=tool_data["description"],
            input_schema=tool_data.get("inputSchema", {}),
            output_schema=tool_data.get("outputSchema"),
        )

    # Parse type-specific config
    if handler_type == "http" and "httpConfig" in data:
        cfg = data["httpConfig"]
        handler.http_config = HTTPConfig(
            endpoint=cfg.get("endpoint", handler.endpoint),
            method=cfg.get("method", "POST"),
            headers=cfg.get("headers", {}),
            content_type=cfg.get("contentType", "application/json"),
        )

    if handler_type == "grpc" and "grpcConfig" in data:
        cfg = data["grpcConfig"]
        handler.grpc_config = GRPCConfig(
            endpoint=cfg.get("endpoint", handler.endpoint),
            tls=cfg.get("tls", False),
            tls_cert_path=cfg.get("tlsCertPath"),
            tls_key_path=cfg.get("tlsKeyPath"),
            tls_ca_path=cfg.get("tlsCAPath"),
            tls_insecure_skip_verify=cfg.get("tlsInsecureSkipVerify", False),
        )

    if handler_type == "mcp" and "mcpConfig" in data:
        cfg = data["mcpConfig"]
        handler.mcp_config = MCPConfig(
            transport=cfg.get("transport", "stdio"),
            endpoint=cfg.get("endpoint"),
            command=cfg.get("command"),
            args=cfg.get("args", []),
            work_dir=cfg.get("workDir"),
            env=cfg.get("env", {}),
        )

    if handler_type == "openapi" and "openAPIConfig" in data:
        cfg = data["openAPIConfig"]
        handler.openapi_config = OpenAPIConfig(
            spec_url=cfg["specURL"],
            base_url=cfg.get("baseURL"),
            operation_filter=cfg.get("operationFilter", []),
        )

    return handler
