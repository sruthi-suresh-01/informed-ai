from typing import Any

from loguru import logger as log
from openai.types.chat import ChatCompletionToolParam
from pydantic import BaseModel


def build_function_schema(
    model: type[BaseModel], name: str | None = None, description: str | None = None
) -> ChatCompletionToolParam:
    json_schema = model.model_json_schema(mode="serialization")
    return {
        "type": "function",
        "function": {
            "name": name or f"generate_{model.__name__.lower()}",
            "description": description or "",
            "parameters": flatten_and_clean_schema(json_schema),
        },
    }


SchemaType = dict[str, Any] | list["SchemaType"]


def flatten_and_clean_schema(schema: SchemaType) -> dict[str, Any]:
    """Flatten the schema by resolving $defs and $refs, and remove 'title' fields."""
    if isinstance(schema, dict) and "$defs" in schema:
        definitions = schema.pop("$defs")
        schema = resolve_refs(schema, definitions)
    schema = remove_titles(schema)
    return schema  # type: ignore[return-value]


def resolve_refs(schema: SchemaType, definitions: dict[str, SchemaType]) -> SchemaType:
    """Recursively resolve $refs in the schema using the provided definitions."""
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref_path = schema["$ref"]
            ref_name = ref_path.split("/")[-1]
            if ref_name in definitions:
                return resolve_refs(definitions[ref_name], definitions)
            else:
                raise ValueError(f"Reference {ref_name} not found in definitions")
        else:
            resolved_schema = {}
            for key, value in schema.items():
                resolved_schema[key] = resolve_refs(value, definitions)
            return resolved_schema
    elif isinstance(schema, list):
        return [resolve_refs(item, definitions) for item in schema]
    else:
        return schema


def remove_titles(schema: SchemaType) -> SchemaType:
    """Recursively remove 'title' fields from the schema."""
    if isinstance(schema, dict):
        if "title" in schema:
            del schema["title"]
        for key, value in schema.items():
            schema[key] = remove_titles(value)
    elif isinstance(schema, list):
        return [remove_titles(item) for item in schema]
    return schema
