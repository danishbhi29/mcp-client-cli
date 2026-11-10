# ui/interactive.py
import json
from typing import Any, Dict, List, Optional
from core.validator import validate_schema, format_schema_constraints
from .input_parser import parse_user_input


def display_tools(tools: List[Dict[str, Any]]) -> None:
    """Prints a formatted list of all available MCP tools."""
    print("\n" + "=" * 50)
    print(" 🛠️  AVAILABLE MCP TOOLS")
    print("=" * 50)

    for index, tool in enumerate(tools, start=1):
        name = tool.get("name", "unnamed")
        desc = tool.get("description", "")
        desc_line = f" - {desc}" if desc else ""
        print(f"\n{index}. Tool: {name}{desc_line}")

        schema = tool.get("inputSchema", {})
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        if not properties:
            if "oneOf" in schema:
                print(f"   Schema requires oneOf ({len(schema['oneOf'])} choices).")
            elif "anyOf" in schema:
                print(f"   Schema requires anyOf ({len(schema['anyOf'])} choices).")
            elif "allOf" in schema:
                print(f"   Schema requires allOf ({len(schema['allOf'])} requirements).")
            else:
                print("   (No arguments required)")
            continue

        for prop_name, details in properties.items():
            status = "Required" if prop_name in required else "Optional"
            arg_type = details.get("type", "any")
            default_val = details.get("default")
            default_info = f", default: {default_val}" if default_val is not None else ""
            enum_vals = details.get("enum")
            enum_info = f", options: {enum_vals}" if enum_vals else ""
            constraints = format_schema_constraints(details)
            constraints_str = f", {constraints}" if constraints else ""

            print(f"   - {prop_name}: {arg_type} ({status}{default_info}{enum_info}{constraints_str})")

    print(f"\nTotal Tools Found: {len(tools)}")


def display_resources(resources: List[Dict[str, Any]]) -> None:
    """Prints a formatted list of all available MCP resources."""
    print("\n" + "=" * 50)
    print(" 📦 AVAILABLE MCP RESOURCES")
    print("=" * 50)

    if not resources:
        print("\nNo resources exposed by this server.")
        return

    for index, res in enumerate(resources, start=1):
        name = res.get("name", "unnamed")
        uri = res.get("uri", "")
        mime = res.get("mimeType", "unknown")
        desc = res.get("description", "")
        print(f"\n{index}. Resource: {name}")
        print(f"   URI: {uri}")
        print(f"   MIME Type: {mime}")
        if desc:
            print(f"   Description: {desc}")

    print(f"\nTotal Resources Found: {len(resources)}")


def display_prompts(prompts: List[Dict[str, Any]]) -> None:
    """Prints a formatted list of all available MCP prompts."""
    print("\n" + "=" * 50)
    print(" 📝 AVAILABLE MCP PROMPTS")
    print("=" * 50)

    if not prompts:
        print("\nNo prompts exposed by this server.")
        return

    for index, p in enumerate(prompts, start=1):
        name = p.get("name", "unnamed")
        desc = p.get("description", "")
        args = p.get("arguments", [])
        print(f"\n{index}. Prompt: {name}")
        if desc:
            print(f"   Description: {desc}")
        if args:
            print("   Arguments:")
            for a in args:
                req = "Required" if a.get("required") else "Optional"
                print(f"     - {a.get('name')}: ({req}) {a.get('description', '')}")
        else:
            print("   (No arguments required)")

    print(f"\nTotal Prompts Found: {len(prompts)}")


def collect_tool_arguments(tool: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interactively prompts user to provide arguments for a tool,
    validating types and constraints against its inputSchema.
    """
    schema = tool.get("inputSchema", {})

    # Top-level oneOf or anyOf without direct properties
    properties = schema.get("properties", {})
    if not properties and ("oneOf" in schema or "anyOf" in schema):
        variants_key = "oneOf" if "oneOf" in schema else "anyOf"
        variants = schema[variants_key]
        print(f"\nThis tool supports multiple schema choices ({variants_key}):")
        for i, sub in enumerate(variants, 1):
            title = sub.get("title") or sub.get("description") or f"Option {i}"
            print(f"  {i}. {title}")
        while True:
            choice = input(f"Select choice (1-{len(variants)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(variants):
                return collect_tool_arguments({"inputSchema": variants[int(choice) - 1]})
            print(f"Please enter a valid choice between 1 and {len(variants)}.")

    required = schema.get("required", [])
    arguments: Dict[str, Any] = {}

    for name, details in properties.items():
        description = details.get("description", "")
        arg_type = details.get("type", "string")
        enum_values = details.get("enum")
        default_value = details.get("default")
        sub_properties = details.get("properties")

        constraints = format_schema_constraints(details)
        constraint_hint = f" [{constraints}]" if constraints else ""

        while True:
            if enum_values:
                print(f"Available options: {enum_values}")
            if default_value is not None:
                print(f"Default value: {default_value}")

            if default_value is not None:
                prompt_label = f"Default: {default_value}{constraint_hint}, Enter to use default"
            elif arg_type == "object" and sub_properties:
                if name in required:
                    prompt_label = f"Required{constraint_hint}: Enter JSON or press Enter to fill fields"
                else:
                    prompt_label = f"Optional{constraint_hint}: Enter JSON, 'i' to fill fields, or Enter to skip"
            elif name in required:
                prompt_label = f"Required{constraint_hint}"
            else:
                prompt_label = f"Optional{constraint_hint}, Enter to skip"

            value = input(f"\n{name} ({description}) [{prompt_label}]: ").strip()

            # Empty input handling
            if value == "":
                if default_value is not None:
                    default_errors = validate_schema(default_value, details, name)
                    if default_errors:
                        print(f"❌ Default value failed validation: {default_errors}")
                    else:
                        arguments[name] = default_value
                        print(f"Using default: {default_value}")
                        break
                elif arg_type == "object" and sub_properties and name in required:
                    print(f"\n--- Fill fields for '{name}' ---")
                    arguments[name] = collect_tool_arguments({"inputSchema": details})
                    break
                elif name in required:
                    print(f"'{name}' is required. Try again!")
                    continue
                else:
                    # Optional field skipped
                    break

            # Interactive nested object fill
            if arg_type == "object" and sub_properties and value.lower() in ("i", "interactive"):
                print(f"\n--- Fill fields for '{name}' ---")
                arguments[name] = collect_tool_arguments({"inputSchema": details})
                break

            # Parse user input
            parsed_value, parse_error = parse_user_input(value, details)
            if parse_error:
                print(f"Input Error: {parse_error}")
                continue

            # Full schema validation
            val_errors = validate_schema(parsed_value, details, name)
            if val_errors:
                print(f"\n❌ Validation Error for '{name}':")
                for err in val_errors:
                    print(f"   - {err}")
                print("Please enter a valid value.")
                continue

            arguments[name] = parsed_value
            break

    # Root schema check
    root_errors = validate_schema(arguments, schema, "arguments")
    if root_errors:
        print("\n⚠️ Root Arguments Schema Validation Warning:")
        for err in root_errors:
            print(f"   - {err}")

    return arguments


def collect_prompt_arguments(prompt: Dict[str, Any]) -> Dict[str, str]:
    """Prompts the user to provide string values for prompt parameters."""
    declared_args = prompt.get("arguments", [])
    if not declared_args:
        return {}

    args: Dict[str, str] = {}
    print(f"\nEnter arguments for prompt '{prompt.get('name')}':")
    for arg in declared_args:
        name = arg.get("name")
        desc = arg.get("description", "")
        req = arg.get("required", False)
        status = "Required" if req else "Optional, Enter to skip"

        while True:
            val = input(f"  {name} ({desc}) [{status}]: ").strip()
            if not val:
                if req:
                    print(f"  ❌ '{name}' is required!")
                    continue
                break
            args[name] = val
            break
    return args


def display_tool_result(result: Dict[str, Any]) -> None:
    """Formats and prints the result of a tool execution."""
    if result.get("isError"):
        print("\n❌ Tool Execution Failed!")
    else:
        print("\n✅ Tool Executed Successfully!")

    for item in result.get("content", []):
        item_type = item.get("type")
        if item_type == "text":
            print(f"\nResult:\n{item.get('text')}")
        elif item_type == "image":
            print(f"\nResult [Image]: MIME '{item.get('mimeType')}' (data length: {len(item.get('data', ''))})")
        elif item_type == "resource":
            res = item.get("resource", {})
            print(f"\nResult [Embedded Resource]: URI: {res.get('uri')}")
            if "text" in res:
                print(res["text"])
        else:
            print(f"\nResult [{item_type}]: {item}")


def display_resource_content(contents: List[Dict[str, Any]]) -> None:
    """Displays resource content returned from server."""
    if not contents:
        print("\n(No content returned for this resource)")
        return

    for c in contents:
        uri = c.get("uri", "")
        mime = c.get("mimeType", "")
        print(f"\n--- Resource Content for: {uri} ({mime}) ---")
        if "text" in c:
            print(c["text"])
        elif "blob" in c:
            blob = c["blob"]
            print(f"[Binary Base64 Blob, length: {len(blob)} chars]")
        else:
            print(c)


def display_prompt_result(result: Dict[str, Any]) -> None:
    """Displays prompt template render result."""
    desc = result.get("description")
    if desc:
        print(f"\nPrompt Description: {desc}")

    messages = result.get("messages", [])
    print(f"\nRendered Prompt Messages ({len(messages)}):")
    for i, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown")
        content = msg.get("content", {})
        if isinstance(content, dict) and content.get("type") == "text":
            text = content.get("text", "")
        elif isinstance(content, str):
            text = content
        else:
            text = json.dumps(content)
        print(f"\n[{role.upper()}]:\n{text}")
