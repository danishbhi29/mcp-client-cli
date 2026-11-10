# core/protocol.py
from typing import Any, Dict, Optional


class MCPError(Exception):
    """Raised when an MCP server returns a JSON-RPC error."""
    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        super().__init__(f"MCP Error [{code}]: {message}")
        self.code = code
        self.message = message
        self.data = data


class MCPTransportError(Exception):
    """Raised when communication with the MCP server fails or connection is closed."""
    pass


class MCPValidationError(Exception):
    """Raised when arguments fail schema validation."""
    def __init__(self, errors: list):
        super().__init__("; ".join(errors))
        self.errors = errors


def create_request(method: str, params: Optional[Dict[str, Any]] = None, request_id: int = 1) -> Dict[str, Any]:
    """Creates a standard JSON-RPC 2.0 request payload."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params if params is not None else {},
    }


def create_notification(method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Creates a standard JSON-RPC 2.0 notification payload (no id)."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
    }
    if params is not None:
        payload["params"] = params
    return payload
