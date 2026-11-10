# client/tools.py
from typing import Any, Dict, List, Optional


class ToolManager:
    """
    Manages MCP Tools: discovery and dynamic execution.
    """

    def __init__(self, client):
        self._client = client

    def list(self) -> List[Dict[str, Any]]:
        """Discovers and returns all available tools from the MCP server."""
        response = self._client.send_request("tools/list")
        result = response.get("result", {})
        return result.get("tools", [])

    def get(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Finds a tool definition by name."""
        tools = self.list()
        for tool in tools:
            if tool.get("name") == tool_name:
                return tool
        return None

    def call(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a tool on the MCP server with the provided arguments.
        Returns the raw tool result dict (e.g. {"content": [...], "isError": bool}).
        """
        response = self._client.send_request(
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": arguments or {},
            },
        )
        return response.get("result", {})
