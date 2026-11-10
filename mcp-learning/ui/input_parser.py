# ui/input_parser.py
import json
from typing import Any, Dict, Optional, Tuple


def parse_user_input(value: str, details: Dict[str, Any]) -> Tuple[Optional[Any], Optional[str]]:
    """
    Parses a raw CLI string into the appropriate Python type according to the schema details.
    Returns (parsed_value, error_message).
    If error_message is None, parsing succeeded.
    """
    arg_type = details.get("type")

    # Boolean parsing
    if arg_type == "boolean":
        val_lower = value.lower()
        if val_lower in ("true", "1", "yes", "y"):
            return True, None
        elif val_lower in ("false", "0", "no", "n"):
            return False, None
        return None, "Invalid boolean! Enter 'true' or 'false'."

    # Integer parsing
    if arg_type == "integer":
        try:
            return int(value), None
        except ValueError:
            return None, "Invalid input! Expected an integer (e.g. 10)."

    # Number (float/int) parsing
    if arg_type == "number":
        try:
            return float(value) if "." in value else int(value), None
        except ValueError:
            return None, "Invalid input! Expected a number (e.g. 3.14 or 10)."

    # Array parsing
    if arg_type == "array":
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed, None
            return None, "Invalid array! Must be a JSON array like: [\"item1\", \"item2\"]"
        except json.JSONDecodeError:
            # Allow comma-separated strings as convenient CLI input
            if not value.startswith("[") and not value.startswith("{"):
                items = [x.strip() for x in value.split(",") if x.strip()]
                item_type = details.get("items", {}).get("type")
                if item_type == "integer":
                    try:
                        return [int(x) for x in items], None
                    except ValueError:
                        return None, "Invalid array items! Expected integers."
                elif item_type == "number":
                    try:
                        return [float(x) for x in items], None
                    except ValueError:
                        return None, "Invalid array items! Expected numbers."
                return items, None
            return None, "Invalid JSON array! Example: [\"item1\", \"item2\"] or item1, item2"

    # Object parsing
    if arg_type == "object":
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed, None
            return None, "Invalid object! Must be a JSON object like: {\"key\": \"value\"}"
        except json.JSONDecodeError:
            return None, "Invalid JSON object! Example: {\"key\": \"value\"}"

    # String parsing
    if arg_type == "string":
        return value, None

    # Flexible fallback parsing for schemas with oneOf/anyOf/allOf or unspecified type
    val_lower = value.lower()
    if val_lower in ("true", "1"):
        return True, None
    if val_lower in ("false", "0"):
        return False, None

    try:
        return json.loads(value), None
    except json.JSONDecodeError:
        pass

    try:
        return int(value), None
    except ValueError:
        pass

    try:
        return float(value), None
    except ValueError:
        pass

    return value, None
