# client/mcp_client.py
from typing import Any, Dict, List, Optional
from core.protocol import MCPError, create_request, create_notification
from core.transport import StdioTransport
from config.settings import (
    SERVER_COMMAND,
    PROTOCOL_VERSION,
    CLIENT_INFO,
    CLIENT_CAPABILITIES,
)
from .tools import ToolManager
from .resources import ResourceManager
from .prompts import PromptManager


class MCPClient:
    """
    Main client coordinator for Model Context Protocol (MCP).
    Provides access to Tools, Resources, and Prompts via sub-managers.
    """

    def __init__(
        self,
        command: Optional[List[str]] = None,
        protocol_version: str = PROTOCOL_VERSION,
        client_info: Optional[Dict[str, str]] = None,
    ):
        self.command = command or SERVER_COMMAND
        self.protocol_version = protocol_version
        self.client_info = client_info or CLIENT_INFO

        self.transport = StdioTransport(self.command)
        self._request_id = 1
        self.server_info: Dict[str, Any] = {}
        self.server_capabilities: Dict[str, Any] = {}

        # Sub-Managers
        self.tools = ToolManager(self)
        self.resources = ResourceManager(self)
        self.prompts = PromptManager(self)

    def _next_id(self) -> int:
        req_id = self._request_id
        self._request_id += 1
        return req_id

    def connect(self) -> Dict[str, Any]:
        """
        Starts transport, conducts the MCP handshake:
        1. Sends 'initialize'
        2. Validates server response
        3. Sends 'notifications/initialized'
        Returns the server's initialize result.
        """
        self.transport.start()

        # Step 1: Handshake Initialize
        init_req = create_request(
            method="initialize",
            params={
                "protocolVersion": self.protocol_version,
                "capabilities": CLIENT_CAPABILITIES,
                "clientInfo": self.client_info,
            },
            request_id=self._next_id(),
        )
        self.transport.send(init_req)
        response = self.transport.read_response(init_req["id"])

        if "error" in response:
            err = response["error"]
            raise MCPError(err.get("code", -1), err.get("message", "Init failed"), err.get("data"))

        init_result = response.get("result", {})
        self.server_info = init_result.get("serverInfo", {})
        self.server_capabilities = init_result.get("capabilities", {})

        # Step 2: Notify server that initialization is complete
        notify_msg = create_notification("notifications/initialized")
        self.transport.send(notify_msg)

        return init_result

    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sends a JSON-RPC request and returns the validated response.
        Raises MCPError if the server returned an error object.
        """
        req_id = self._next_id()
        request = create_request(method, params, req_id)
        self.transport.send(request)
        response = self.transport.read_response(req_id)

        if "error" in response:
            err = response["error"]
            raise MCPError(
                code=err.get("code", -1),
                message=err.get("message", "Unknown error"),
                data=err.get("data"),
            )

        return response

    def send_notification(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Sends a JSON-RPC notification (no response expected)."""
        payload = create_notification(method, params)
        self.transport.send(payload)

    def close(self) -> None:
        """Closes the client and terminates underlying server transport."""
        self.transport.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
