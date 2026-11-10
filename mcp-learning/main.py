# main.py
import sys
from client import MCPClient
from core.protocol import MCPError, MCPTransportError
from ui import (
    display_tools,
    display_resources,
    display_prompts,
    collect_tool_arguments,
    collect_prompt_arguments,
    display_tool_result,
    display_resource_content,
    display_prompt_result,
)


def run_tools_menu(client: MCPClient) -> None:
    """Sub-menu for discovering and executing MCP tools."""
    try:
        tools = client.tools.list()
    except MCPError as e:
        print(f"\n❌ Error listing tools: {e}")
        return

    if not tools:
        print("\nNo tools available on this server.")
        return

    display_tools(tools)

    while True:
        choice = input("\nEnter tool number (or 'b' to back, 'q' to quit): ").strip().lower()

        if choice == "b":
            break
        if choice == "q":
            sys.exit(0)

        if not choice.isdigit() or not (1 <= int(choice) <= len(tools)):
            print(f"Invalid selection! Please enter a number between 1 and {len(tools)}.")
            continue

        selected_tool = tools[int(choice) - 1]
        print(f"\n--- Selected Tool: {selected_tool['name']} ---")

        arguments = collect_tool_arguments(selected_tool)
        print("\nSubmitting Arguments:", arguments)
        print("Executing tool...")

        try:
            result = client.tools.call(selected_tool["name"], arguments)
            display_tool_result(result)
        except MCPError as e:
            print(f"\n❌ MCP Error: {e}")


def run_resources_menu(client: MCPClient) -> None:
    """Sub-menu for listing and reading MCP resources."""
    try:
        resources = client.resources.list()
    except MCPError as e:
        print(f"\n❌ Error listing resources: {e}")
        return

    display_resources(resources)

    # Also check templates
    try:
        templates = client.resources.list_templates()
        if templates:
            print(f"\nResource Templates ({len(templates)} available):")
            for t in templates:
                print(f"  - {t.get('name')}: URI Template '{t.get('uriTemplate')}'")
    except Exception:
        pass

    if not resources:
        return

    while True:
        choice = input("\nEnter resource number to read (or 'b' to back, 'q' to quit): ").strip().lower()

        if choice == "b":
            break
        if choice == "q":
            sys.exit(0)

        if not choice.isdigit() or not (1 <= int(choice) <= len(resources)):
            print(f"Invalid selection! Please enter a number between 1 and {len(resources)}.")
            continue

        selected_res = resources[int(choice) - 1]
        uri = selected_res.get("uri")
        print(f"\nReading Resource: {uri} ...")

        try:
            contents = client.resources.read(uri)
            display_resource_content(contents)
        except MCPError as e:
            print(f"\n❌ MCP Error reading resource: {e}")


def run_prompts_menu(client: MCPClient) -> None:
    """Sub-menu for listing and retrieving MCP prompt templates."""
    try:
        prompts = client.prompts.list()
    except MCPError as e:
        print(f"\n❌ Error listing prompts: {e}")
        return

    display_prompts(prompts)

    if not prompts:
        return

    while True:
        choice = input("\nEnter prompt number to retrieve (or 'b' to back, 'q' to quit): ").strip().lower()

        if choice == "b":
            break
        if choice == "q":
            sys.exit(0)

        if not choice.isdigit() or not (1 <= int(choice) <= len(prompts)):
            print(f"Invalid selection! Please enter a number between 1 and {len(prompts)}.")
            continue

        selected_prompt = prompts[int(choice) - 1]
        args = collect_prompt_arguments(selected_prompt)
        print(f"\nRetrieving prompt '{selected_prompt['name']}'...")

        try:
            prompt_res = client.prompts.get(selected_prompt["name"], args)
            display_prompt_result(prompt_res)
        except MCPError as e:
            print(f"\n❌ MCP Error getting prompt: {e}")


def main() -> None:
    """Main client entrypoint."""
    print("=" * 60)
    print(" 🚀 Python Model Context Protocol (MCP) Client")
    print("=" * 60)
    print("Connecting to MCP Server...")

    client = MCPClient()

    try:
        init_res = client.connect()
        server_name = client.server_info.get("name", "Unknown Server")
        server_ver = client.server_info.get("version", "")
        proto_ver = init_res.get("protocolVersion", client.protocol_version)

        print(f"✅ Connected to: {server_name} (v{server_ver})")
        print(f"📡 Protocol Version: {proto_ver}")

        while True:
            print("\n" + "=" * 40)
            print("         MCP MAIN MENU")
            print("=" * 40)
            print("1. 🛠️  Tools (Explore & Run)")
            print("2. 📦 Resources (Explore & Read)")
            print("3. 📝 Prompts (Explore & Retrieve)")
            print("q. 🚪 Quit")

            selection = input("\nSelect an option (1-3, q): ").strip().lower()

            if selection == "1":
                run_tools_menu(client)
            elif selection == "2":
                run_resources_menu(client)
            elif selection == "3":
                run_prompts_menu(client)
            elif selection == "q":
                print("\nExiting MCP Client. Goodbye!")
                break
            else:
                print("Invalid option! Please select 1, 2, 3, or q.")

    except MCPTransportError as te:
        print(f"\n❌ Transport Error: {te}")
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
    finally:
        print("\nCleaning up and closing MCP server...")
        client.close()
        print("MCP Server closed cleanly.")


if __name__ == "__main__":
    main()
