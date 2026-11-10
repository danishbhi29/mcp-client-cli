# Python Model Context Protocol (MCP) Client 🚀

A lightweight, modular, and dependency-free Python client for the **Model Context Protocol (MCP)**. This client connects to MCP servers over standard input/output (`stdio`), validates payloads against JSON Schemas, and provides an interactive terminal UI to explore tools, resources, and prompts.

---

## ✨ Features

- **Standard Protocol Support:** Implements the official MCP handshake (`initialize` and `notifications/initialized`).
- **Stdio Subprocess Transport:** Manages server process lifecycle, JSON-RPC correlation, and stream communication.
- **Robust JSON Schema Validator:** Built-in validator supporting primitives, numeric ranges, string lengths, array/object constraints, and composite schemas (`oneOf`, `anyOf`, `allOf`, `enum`).
- **Full MCP Primitives Support:**
  - 🛠️ **Tools:** Dynamic discovery (`tools/list`) and interactive invocation (`tools/call`).
  - 📦 **Resources:** Listing (`resources/list`), reading contents (`resources/read`), and template inspection (`resources/templates/list`).
  - 📝 **Prompts:** Discovery (`prompts/list`) and retrieval (`prompts/get`).
- **Interactive Terminal UI:** User-friendly CLI with live argument type-casting and validation.
- **Zero External Core Dependencies:** Built using Python 3.10+ standard libraries (`json`, `subprocess`, etc.).

---

## 📁 Project Structure

```text
├── .gitignore
├── README.md
├── requirements.txt
└── mcp-learning/
    ├── main.py              # Interactive CLI application
    ├── test_suite.py        # Automated test suite
    ├── config/
    │   └── settings.py      # Server command & protocol settings
    ├── core/
    │   ├── protocol.py      # JSON-RPC builders and error handling
    │   ├── transport.py     # Subprocess stdio transport
    │   └── validator.py     # Custom JSON Schema validator
    ├── client/
    │   ├── mcp_client.py    # Main MCP client orchestrator
    │   ├── tools.py         # ToolManager
    │   ├── resources.py     # ResourceManager
    │   └── prompts.py       # PromptManager
    └── ui/
        ├── input_parser.py  # User input type parser & caster
        └── interactive.py   # Terminal menus and rendering
```

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+**
2. **Node.js & npm** (required to run default reference servers via `npx`):
   ```bash
   node --version
   npx --version
   ```

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/danishbhi29/mcp-client-cli.git
   cd mcp-client-cli
   ```

2. **(Optional) Set up a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

---

## 💻 Usage

### 1. Run the Interactive Client
Run the main CLI from the `mcp-learning` directory:
```bash
python mcp-learning/main.py
```
By default, it launches the reference server `@modelcontextprotocol/server-everything` via `npx` and displays the interactive main menu.

### 2. Run the Test Suite
To verify protocol handshake, schema validation, and tool invocation:
```bash
python mcp-learning/test_suite.py
```

---

## ⚙️ Configuration

Server configurations can be modified in `mcp-learning/config/settings.py`:
- `SERVER_COMMAND`: Command to launch the target MCP server (default: `npx -y @modelcontextprotocol/server-everything`).
- `PROTOCOL_VERSION`: Target MCP protocol version (default: `2025-06-18`).

---

## 📄 License
MIT License. Free to use and modify.
