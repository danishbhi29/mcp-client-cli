# client/prompts.py
from typing import Any, Dict, List, Optional


class PromptManager:
    """
    Manages MCP Prompts: template discovery and retrieval with arguments.
    """

    def __init__(self, client):
        self._client = client

    def list(self) -> List[Dict[str, Any]]:
        """Lists all prompt templates declared by the MCP server."""
        response = self._client.send_request("prompts/list")
        result = response.get("result", {})
        return result.get("prompts", [])

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
