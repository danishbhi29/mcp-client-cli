# client/prompts.py
from typing import Any, Dict, List, Optional
from core.protocol import MCPError


class PromptManager:
    """
    Manages MCP Prompts: template discovery and retrieval with arguments.
    """

    def __init__(self, client):
        self._client = client

    @property
    def is_supported(self) -> bool:
        """Returns True if the connected server advertises prompt capabilities."""
        return "prompts" in getattr(self._client, "server_capabilities", {})

    def list(self) -> List[Dict[str, Any]]:
        """Lists all prompt templates declared by the MCP server."""
        if not self.is_supported:
            return []
        try:
            response = self._client.send_request("prompts/list")
            result = response.get("result", {})
            return result.get("prompts", [])
        except MCPError as e:
            if e.code == -32601:  # Method not found
                return []
            raise

    def get(self, prompt_name: str, arguments: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Retrieves a rendered prompt template with arguments.
        Returns dict containing 'description' and 'messages' list.
        """
        response = self._client.send_request(
            method="prompts/get",
            params={
                "name": prompt_name,
                "arguments": arguments or {},
            },
        )
        return response.get("result", {})
