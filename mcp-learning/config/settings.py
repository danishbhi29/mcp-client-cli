# config/settings.py
import os
import shutil

# Resolve npx path automatically or fallback to Windows default
NPX_PATH = shutil.which("npx") or shutil.which("npx.cmd") or r"C:\Program Files\nodejs\npx.cmd"

# Default MCP Server Command (MCP Filesystem Server pointing to the workspace root)
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

SERVER_COMMAND = [
    NPX_PATH,
    "-y",
    "@modelcontextprotocol/server-filesystem",
    WORKSPACE_ROOT,
]

# MCP Protocol Configuration
PROTOCOL_VERSION = "2025-06-18"

# Client Identification
CLIENT_INFO = {
    "name": "python-mcp-client",
    "version": "1.0.0",
}

# Client Capabilities (Keep empty unless server-to-client handlers are implemented)
CLIENT_CAPABILITIES = {}
