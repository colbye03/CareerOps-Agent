"""Validated, versioned contracts shared by CLI and engine."""
import json
from importlib.resources import files
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(kind, value):
    schema = json.loads(files("careerops").joinpath(f"resources/schemas/{kind}.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
    if kind == "role-pack":
        dimensions = value["dimensions"]
        if len({d["id"] for d in dimensions}) != len(dimensions):
            raise ValueError("dimension IDs must be unique")
        if abs(sum(d["weight"] for d in dimensions) - 1) > 1e-8:
            raise ValueError("dimension weights must sum to one")
    if kind == "candidate":
        if value["search_policy"]["maybe_threshold"] > value["search_policy"]["apply_threshold"]:
            raise ValueError("maybe threshold must not exceed apply threshold")
    if kind == "job" and value.get("salary") and value["salary"]["min"] > value["salary"]["max"]:
        raise ValueError("salary minimum must not exceed maximum")
    if kind == "evidence":
        if len({e["id"] for e in value}) != len(value):
            raise ValueError("evidence IDs must be unique")
    return value


def starter(kind, name):
    return json.loads(files("careerops").joinpath(f"resources/{kind}/{name}.json").read_text())
