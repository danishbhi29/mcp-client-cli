# client/resources.py
from typing import Any, Dict, List, Optional
from core.protocol import MCPError


class ResourceManager:
    """
    Manages MCP Resources: reading static/dynamic context, logs, files, and templates.
    """

    def __init__(self, client):
        self._client = client

    @property
    def is_supported(self) -> bool:
        """Returns True if the connected server advertises resource capabilities."""
        return "resources" in getattr(self._client, "server_capabilities", {})

    def list(self) -> List[Dict[str, Any]]:
        """Lists all resources available on the MCP server."""
        if not self.is_supported:
            return []
        try:
            response = self._client.send_request("resources/list")
            result = response.get("result", {})
            return result.get("resources", [])
        except MCPError as e:
            if e.code == -32601:
                return []
            raise

    def list_templates(self) -> List[Dict[str, Any]]:
        """Lists all resource templates available on the MCP server."""
        if not self.is_supported:
            return []
        try:
            response = self._client.send_request("resources/templates/list")
            result = response.get("result", {})
            return result.get("resourceTemplates", [])
        except MCPError as e:
            if e.code == -32601:
                return []
            raise

    def read(self, uri: str) -> List[Dict[str, Any]]:
        """
        Reads the contents of a specific resource by its URI.
        Returns a list of content objects (each having 'uri', 'mimeType', and 'text' or 'blob').
        """
        response = self._client.send_request(
            method="resources/read",
            params={"uri": uri},
        )
        result = response.get("result", {})
        return result.get("contents", [])

    def subscribe(self, uri: str) -> Dict[str, Any]:
        """Subscribes to updates for a specific resource."""
        response = self._client.send_request(
            method="resources/subscribe",
            params={"uri": uri},
        )
        return response.get("result", {})

    def unsubscribe(self, uri: str) -> Dict[str, Any]:
        """Unsubscribes from updates for a specific resource."""
        response = self._client.send_request(
            method="resources/unsubscribe",
            params={"uri": uri},
        )
        return response.get("result", {})
