"""Validate crew output in Python instead of via the provider's structured-output schema.

Why this exists. crewAI's ``output_pydantic`` is convenient: it serialises the model to a JSON
Schema and makes the provider enforce it. But that schema is the provider's problem now, and
Anthropic rejects nested ones outright ("Schema is too complex"). The limit is not documented as
a number you can design against, so tuning field counts under it is guesswork that breaks again
the next time a model is added.

So the schema never leaves this process. The task prompt carries a rendered *example* of the
shape — plain text, no provider involvement — and the output is parsed and validated here. The
guardrail is not weaker: pydantic still rejects malformed output. It just fires one step later,
where we control it, and it works identically on Anthropic, OpenAI, Gemini or a local model.
"""

from __future__ import annotations

import json
import re
from typing import Literal, TypeVar, get_args, get_origin

import json_repair
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _render_type(annotation) -> str:
    """Describe a type the way a model can act on it.

    Enumerated values are the whole point of a Literal — rendering it as "one of" without
    listing them tells the model nothing, and it will invent a value that then fails validation.
    """
    origin = get_origin(annotation)

    if origin is Literal:
        return " | ".join(f'"{v}"' for v in get_args(annotation))
    if origin in (list, list):
        inner = get_args(annotation)
        return f"[{_render_type(inner[0])}, ...]" if inner else "[...]"
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return "{" + ", ".join(f'"{n}": ...' for n in annotation.model_fields) + "}"
    return getattr(annotation, "__name__", str(annotation)).replace("typing.", "")


def shape_hint(model: type[BaseModel]) -> str:
    """A compact, human-readable rendering of the expected JSON, for the task prompt.

    Generated from the model itself, so the prompt and the type it is validated against cannot
    drift apart — the failure mode of writing the shape into the YAML by hand. Field descriptions
    are carried through: they are the real instructions, worth more than the type names.
    """
    lines = []
    for name, field in model.model_fields.items():
        rendered = _render_type(field.annotation)
        note = f"  // {field.description}" if field.description else ""
        lines.append(f'  "{name}": {rendered},{note}')
    return "{\n" + "\n".join(lines) + "\n}"


def extract_json(raw: str) -> str:
    """Pull the JSON object out of whatever the model wrapped it in."""
    fenced = _FENCE.search(raw)
    if fenced:
        return fenced.group(1).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end > start:
        return raw[start : end + 1]
    return raw.strip()


def parse_as(model: type[T], raw: str) -> T:
    """Parse and validate, tolerating the two ways LLM-authored JSON goes wrong.

    *Syntax*: a fifteen-thousand-character JSON object written token by token will eventually
    drop a comma or leave a quote unescaped. That is not a prompt failure to be scolded out of
    the model — it is a property of generating structured text without a parser in the loop.
    json_repair fixes the punctuation deterministically.

    *Semantics*: the model writes "HIGH — because the full text was unavailable" where an enum
    was asked for, or a paragraph where a list was. Those are handled by coercing validators on
    the models themselves (see schemas.py), because the intent is recoverable and rejecting the
    whole run over it wastes an entire crew execution.

    What is NOT tolerated: invented fields, missing required ones, or output that is not JSON at
    all. Those raise, with the offending text attached.
    """
    text = extract_json(raw)

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        # json_repair closes an object the model left unterminated — a report that ran into the
        # output-token ceiling mid-write is recovered up to the last complete field rather than
        # discarding an entire (paid) crew run. Missing required fields still raise below.
        try:
            payload = json.loads(json_repair.repair_json(text))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(
                f"Output was not recoverable JSON for {model.__name__}: {exc}\n\n"
                f"--- raw output (first 2000 chars) ---\n{raw[:2000]}"
            ) from exc

    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(
            f"Parsed JSON did not match {model.__name__}: {exc}\n\n"
            f"--- raw output (first 2000 chars) ---\n{raw[:2000]}"
        ) from exc
