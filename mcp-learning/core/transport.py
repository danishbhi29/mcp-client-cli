# core/transport.py
import json
import subprocess
from typing import Any, Dict, List, Optional
from .protocol import MCPTransportError


class StdioTransport:
    """
    Manages low-level stdio communication with an MCP server subprocess.
    Handles process lifecycle, JSON serialization, and JSON-RPC stream reading.
    """

    def __init__(self, command: List[str]):
        self.command = command
        self.process: Optional[subprocess.Popen] = None

    def start(self) -> None:
        """Starts the server process."""
        if self.process is not None and self.process.poll() is None:
            return  # Already running

        try:
            self.process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=None,
                text=True,
                encoding="utf-8",
                bufsize=1,
            )
        except Exception as e:
            raise MCPTransportError(f"Failed to start server process: {e}") from e

    def is_running(self) -> bool:
        """Returns True if the subprocess is currently running."""
        return self.process is not None and self.process.poll() is None

    def send(self, payload: Dict[str, Any]) -> None:
        """Sends a JSON-RPC payload to the server's stdin."""
        if not self.is_running():
            raise MCPTransportError("Cannot send payload: Server process is not running.")

        try:
            message = json.dumps(payload)
            self.process.stdin.write(message + "\n")
            self.process.stdin.flush()
        except Exception as e:
            raise MCPTransportError(f"Failed to write to server stdin: {e}") from e

    def read_response(self, request_id: int) -> Dict[str, Any]:
        """
        Reads from server stdout until a response with matching request_id is found.
        Discards server notifications and log messages.
        """
        if not self.is_running():
            raise MCPTransportError("Cannot read: Server process is not running.")

        while True:
            line = self.process.stdout.readline()

            if not line:
                raise MCPTransportError("Server closed the connection (EOF received).")

            line = line.strip()
            if not line:
                continue

            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                # Discard non-JSON lines (e.g. server debug prints)
                continue

            # Ignore notifications and messages with non-matching request_id
            if message.get("id") != request_id:
                continue

            # Return valid JSON-RPC response (containing result or error)
            if "result" in message or "error" in message:
                return message

    def close(self) -> None:
        """Gracefully terminates the server subprocess."""
        if self.process is not None and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except (subprocess.TimeoutExpired, Exception):
                try:
                    self.process.kill()
                    self.process.wait(timeout=1)
                except Exception:
                    pass
            finally:
                self.process = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
