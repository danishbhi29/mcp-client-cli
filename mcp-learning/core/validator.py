# core/validator.py
from typing import Any, Dict, List


def validate_schema(value: Any, schema: Dict[str, Any], path: str = "value") -> List[str]:
    """
    Validates a value against a JSON Schema supporting:
    - type (string, integer, number, boolean, array, object, null)
    - minimum / maximum / exclusiveMinimum / exclusiveMaximum (Number range)
    - minLength / maxLength (String length)
    - minItems / maxItems / items (Array element constraints & recursion)
    - required / properties / additionalProperties (Object field constraints)
    - oneOf (Exactly one schema match)
    - anyOf (At least one schema match)
    - allOf (All schemas must match)
    - enum (Allowed values list)

    Returns a list of error message strings. An empty list indicates valid data.
    """
    errors: List[str] = []
    if not isinstance(schema, dict) or not schema:
        return errors

    # Type validation
    if "type" in schema:
        expected = schema["type"]
        types = [expected] if isinstance(expected, str) else expected
        type_matched = False
        for t in types:
            if t == "string" and isinstance(value, str):
                type_matched = True
            elif t == "integer" and isinstance(value, int) and not isinstance(value, bool):
                type_matched = True
            elif t == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
                type_matched = True
            elif t == "boolean" and isinstance(value, bool):
                type_matched = True
            elif t == "array" and isinstance(value, list):
                type_matched = True
            elif t == "object" and isinstance(value, dict):
                type_matched = True
            elif t == "null" and value is None:
                type_matched = True

        if not type_matched:
            errors.append(f"'{path}': Expected type '{expected}', got '{type(value).__name__}'")
            return errors  # Halt further checks if base type does not match

    # Numeric validations: minimum / maximum / exclusiveMinimum / exclusiveMaximum
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"'{path}': Value {value} is less than minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"'{path}': Value {value} is greater than maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema:
            ex_min = schema["exclusiveMinimum"]
            if isinstance(ex_min, bool) and ex_min and "minimum" in schema:
                if value <= schema["minimum"]:
                    errors.append(f"'{path}': Value {value} must be strictly greater than {schema['minimum']}")
            elif isinstance(ex_min, (int, float)) and value <= ex_min:
                errors.append(f"'{path}': Value {value} must be strictly greater than {ex_min}")
        if "exclusiveMaximum" in schema:
            ex_max = schema["exclusiveMaximum"]
            if isinstance(ex_max, bool) and ex_max and "maximum" in schema:
                if value >= schema["maximum"]:
                    errors.append(f"'{path}': Value {value} must be strictly less than {schema['maximum']}")
            elif isinstance(ex_max, (int, float)) and value >= ex_max:
                errors.append(f"'{path}': Value {value} must be strictly less than {ex_max}")

    # String validations: minLength / maxLength
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"'{path}': Length {len(value)} is less than minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"'{path}': Length {len(value)} is greater than maxLength {schema['maxLength']}")

    # Array validations: minItems / maxItems / items
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"'{path}': Item count {len(value)} is less than minItems {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"'{path}': Item count {len(value)} is greater than maxItems {schema['maxItems']}")
        if "items" in schema and isinstance(schema["items"], dict):
            for i, item in enumerate(value):
                errors.extend(validate_schema(item, schema["items"], f"{path}[{i}]"))

    # Object validations: required / properties / additionalProperties
    if isinstance(value, dict):
        if "required" in schema:
            for req in schema["required"]:
                if req not in value:
                    errors.append(f"'{path}': Missing required property '{req}'")
        props = schema.get("properties", {})
        for k, v in value.items():
            if k in props:
                errors.extend(validate_schema(v, props[k], f"{path}.{k}"))
        extra_keys = set(value.keys()) - set(props.keys())
        add_props = schema.get("additionalProperties")
        if add_props is False and extra_keys:
            errors.append(f"'{path}': Additional properties not allowed: {sorted(list(extra_keys))}")
        elif isinstance(add_props, dict):
            for k in extra_keys:
                errors.extend(validate_schema(value[k], add_props, f"{path}.{k}"))

    # Composite validations: oneOf
    if "oneOf" in schema:
        valid_count = 0
        sub_errors = []
        for i, sub in enumerate(schema["oneOf"]):
            errs = validate_schema(value, sub, path)
            if not errs:
                valid_count += 1
            else:
                sub_errors.append(f"Option {i+1}: {', '.join(errs)}")
        if valid_count != 1:
            errors.append(f"'{path}': Must match exactly ONE schema in 'oneOf' (matched {valid_count}). [{'; '.join(sub_errors)}]")

    # Composite validations: anyOf
    if "anyOf" in schema:
        matched = False
        sub_errors = []
        for i, sub in enumerate(schema["anyOf"]):
            errs = validate_schema(value, sub, path)
            if not errs:
                matched = True
                break
            else:
                sub_errors.append(f"Option {i+1}: {', '.join(errs)}")
        if not matched:
            errors.append(f"'{path}': Must match at least ONE schema in 'anyOf'. [{'; '.join(sub_errors)}]")

    # Composite validations: allOf
    if "allOf" in schema:
        for i, sub in enumerate(schema["allOf"]):
            errs = validate_schema(value, sub, path)
            if errs:
                errors.append(f"'{path}': Failed 'allOf' requirement (Option {i+1}): {', '.join(errs)}")

    # Enum validation
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"'{path}': Value '{value}' is not in allowed enum options: {schema['enum']}")

    return errors


def format_schema_constraints(schema: Dict[str, Any]) -> str:
    """Generates a concise string of validation constraints for CLI hints."""
    if not isinstance(schema, dict):
        return ""
    constraints = []
    if "minimum" in schema or "maximum" in schema:
        min_v = schema.get("minimum", "-inf")
        max_v = schema.get("maximum", "+inf")
        constraints.append(f"range: [{min_v} to {max_v}]")
    if "minLength" in schema or "maxLength" in schema:
        min_l = schema.get("minLength", 0)
        max_l = schema.get("maxLength", "inf")
        constraints.append(f"length: [{min_l} to {max_l}]")
    if "minItems" in schema or "maxItems" in schema:
        min_i = schema.get("minItems", 0)
        max_i = schema.get("maxItems", "inf")
        constraints.append(f"items: [{min_i} to {max_i}]")
    if schema.get("additionalProperties") is False:
        constraints.append("no extra properties")
    if "oneOf" in schema:
        constraints.append(f"oneOf ({len(schema['oneOf'])} options)")
    if "anyOf" in schema:
        constraints.append(f"anyOf ({len(schema['anyOf'])} options)")
    if "allOf" in schema:
        constraints.append(f"allOf ({len(schema['allOf'])} requirements)")
    return ", ".join(constraints)
