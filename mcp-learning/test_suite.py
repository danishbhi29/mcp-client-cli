# test_suite.py
"""
Automated validation and integration test suite for the refactored MCP client.
Tests:
1. Schema validator (types, numbers, strings, arrays, objects, oneOf/anyOf/allOf)
2. Input parser (booleans, integers, numbers, arrays, json)
3. Live MCP Server connection (handshake, tools listing, tool execution, resources listing, prompts listing)
"""
import sys
import os

# Add mcp-learning to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.validator import validate_schema, format_schema_constraints
from ui.input_parser import parse_user_input
from client import MCPClient


def test_validator():
    print("Testing Validator...")
    # Test numeric range
    schema_num = {"type": "integer", "minimum": 10, "maximum": 20}
    assert validate_schema(15, schema_num) == [], "Should be valid"
    assert len(validate_schema(5, schema_num)) > 0, "5 is < 10, should fail"
    assert len(validate_schema(25, schema_num)) > 0, "25 is > 20, should fail"

    # Test string length
    schema_str = {"type": "string", "minLength": 3, "maxLength": 5}
    assert validate_schema("abc", schema_str) == []
    assert len(validate_schema("a", schema_str)) > 0
    assert len(validate_schema("abcdef", schema_str)) > 0

    # Test array min/max items
    schema_arr = {"type": "array", "minItems": 1, "maxItems": 2, "items": {"type": "integer"}}
    assert validate_schema([1], schema_arr) == []
    assert validate_schema([1, 2], schema_arr) == []
    assert len(validate_schema([], schema_arr)) > 0
    assert len(validate_schema([1, 2, 3], schema_arr)) > 0
    assert len(validate_schema(["not_an_int"], schema_arr)) > 0

    # Test object required & additionalProperties: False
    schema_obj = {
        "type": "object",
        "required": ["name"],
        "properties": {"name": {"type": "string"}},
        "additionalProperties": False,
    }
    assert validate_schema({"name": "Antigravity"}, schema_obj) == []
    assert len(validate_schema({}, schema_obj)) > 0, "Missing required 'name'"
    assert len(validate_schema({"name": "Antigravity", "extra": 123}, schema_obj)) > 0, "Extra property not allowed"

    # Test oneOf
    schema_oneof = {
        "oneOf": [
            {"type": "string"},
            {"type": "integer"}
        ]
    }
    assert validate_schema("hello", schema_oneof) == []
    assert validate_schema(42, schema_oneof) == []
    assert len(validate_schema([], schema_oneof)) > 0

    print("✅ Validator tests passed!")


def test_input_parser():
    print("Testing Input Parser...")
    # Boolean
    val, err = parse_user_input("true", {"type": "boolean"})
    assert val is True and err is None
    val, err = parse_user_input("false", {"type": "boolean"})
    assert val is False and err is None
    val, err = parse_user_input("notabool", {"type": "boolean"})
    assert err is not None

    # Integer
    val, err = parse_user_input("123", {"type": "integer"})
    assert val == 123 and err is None

    # Number
    val, err = parse_user_input("3.14", {"type": "number"})
    assert abs(val - 3.14) < 0.001 and err is None

    # Array (comma separated & JSON)
    val, err = parse_user_input("apple, banana, orange", {"type": "array"})
    assert val == ["apple", "banana", "orange"] and err is None
    val, err = parse_user_input("[1, 2, 3]", {"type": "array"})
    assert val == [1, 2, 3] and err is None

    # Object
    val, err = parse_user_input('{"key": "value"}', {"type": "object"})
    assert val == {"key": "value"} and err is None

    print("✅ Input Parser tests passed!")


def test_live_mcp_client():
    print("Testing Live MCP Client Connection...")
    client = MCPClient()
    try:
        init_result = client.connect()
        assert "serverInfo" in init_result or client.server_info, "Server info should be captured"
        print(f"  Connected to server: {client.server_info.get('name')}")

        # Test Tools
        tools = client.tools.list()
        print(f"  Discovered {len(tools)} tools.")
        assert len(tools) > 0, "Server-everything should return tools"

        # Find echo tool and test call
        echo_tool = next((t for t in tools if t.get("name") == "echo"), None)
        if echo_tool:
            print("  Calling 'echo' tool...")
            res = client.tools.call("echo", {"message": "Antigravity Test"})
            assert not res.get("isError"), f"Echo call failed: {res}"
            content = res.get("content", [])
            assert any("Antigravity Test" in c.get("text", "") for c in content if c.get("type") == "text")
            print("  'echo' tool call verified successfully!")

        # Test Resources
        resources = client.resources.list()
        print(f"  Discovered {len(resources)} resources.")
        if resources:
            first_res = resources[0]
            print(f"  Reading resource: {first_res.get('uri')}")
            content = client.resources.read(first_res.get("uri"))
            assert len(content) > 0, "Resource should return contents"
            print("  Resource read successfully!")

        # Test Prompts
        prompts = client.prompts.list()
        print(f"  Discovered {len(prompts)} prompts.")
        if prompts:
            first_prompt = prompts[0]
            print(f"  Retrieving prompt: {first_prompt.get('name')}")
            # Supply any required args with dummy strings
            req_args = {a["name"]: "test" for a in first_prompt.get("arguments", []) if a.get("required")}
            p_res = client.prompts.get(first_prompt.get("name"), req_args)
            assert "messages" in p_res, "Prompt should return messages"
            print("  Prompt retrieved successfully!")

        print("✅ Live MCP Client tests passed completely!")
    finally:
        print("Closing client...")
        client.close()
        print("Client closed cleanly.")


if __name__ == "__main__":
    test_validator()
    test_input_parser()
    test_live_mcp_client()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! EVERYTHING IS 100% OPERATIONAL.")
