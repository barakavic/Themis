from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from .database import DATABASE_PATH, MATERIAL_UNITS, save_estimate
except ImportError:
    from database import DATABASE_PATH, MATERIAL_UNITS, save_estimate

KNOWLEDGE_BASE_PATH = Path(__file__).with_name("knowledge_base.pl")


def split_top_level(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    in_quotes = False

    for char in text:
        if char == '"':
            in_quotes = not in_quotes
        elif not in_quotes:
            if char in "([":
                depth += 1
            elif char in ")]":
                depth -= 1
            elif char == "," and depth == 0:
                parts.append("".join(current).strip())
                current = []
                continue
        current.append(char)

    if current:
        parts.append("".join(current).strip())

    return parts


def parse_number(value: str) -> float:
    return float(value.strip())


def parse_materials(materials_term: str) -> dict[str, float]:
    match = re.fullmatch(r"materials\((.*)\)", materials_term.strip())
    if not match:
        raise ValueError(f"Unexpected materials term: {materials_term}")

    cement, steel, bricks, timber = split_top_level(match.group(1))
    return {
        "cement": parse_number(cement),
        "steel": parse_number(steel),
        "bricks": parse_number(bricks),
        "timber": parse_number(timber),
    }


def clean_reason_text(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")

    value_text = str(value).strip()
    atom_match = re.fullmatch(r"Atom\('(.+)'\)", value_text)
    if atom_match:
        return atom_match.group(1)

    if value_text.startswith('"') and value_text.endswith('"'):
        return value_text[1:-1]

    if value_text.startswith("b'") and value_text.endswith("'"):
        return value_text[2:-1]

    return value_text


def parse_reasons(reasons_term: str) -> list[str]:
    text = reasons_term.strip()
    if text == "[]":
        return []
    if not (text.startswith("[") and text.endswith("]")):
        return [clean_reason_text(text)]

    items = split_top_level(text[1:-1])
    return [clean_reason_text(item) for item in items]


def parse_result(result_term: Any) -> dict[str, Any]:
    result_text = str(result_term).strip()
    match = re.fullmatch(r"result\((.*)\)", result_text)
    if not match:
        return {"raw": result_text}

    parts = split_top_level(match.group(1))
    if len(parts) != 6:
        return {"raw": result_text}

    area, materials_term, base_cost, final_cost, feasibility, reasons_term = parts
    return {
        "area": parse_number(area),
        "materials": parse_materials(materials_term),
        "base_cost": parse_number(base_cost),
        "final_cost": parse_number(final_cost),
        "feasibility": feasibility.strip(),
        "reasons": parse_reasons(reasons_term),
        "raw": result_text,
    }


def format_currency(value: float) -> str:
    return f"KES {value:,.2f}"


def format_estimate_text(parsed: dict[str, Any], estimate_id: int | None = None) -> str:
    if "area" not in parsed:
        return parsed["raw"]

    lines = [
        "ESTIMATION RESULT",
        "",
        f"Total Area: {parsed['area']:.2f} m^2",
        f"Base Cost: {format_currency(parsed['base_cost'])}",
        f"Final Estimated Cost: {format_currency(parsed['final_cost'])}",
        f"Feasibility Status: {parsed['feasibility'].replace('_', ' ').title()}",
        "",
        "Material Breakdown:",
    ]

    for material, quantity in parsed["materials"].items():
        lines.append(
            f"- {material.capitalize()}: {quantity:.2f} {MATERIAL_UNITS[material]}"
        )

    lines.extend(["", "Explanation:"])
    for reason in parsed["reasons"]:
        lines.append(f"- {reason}")

    if estimate_id is not None:
        lines.extend(["", f"Saved estimate #{estimate_id} to {DATABASE_PATH}."])

    return "\n".join(lines)


def validate_positive_integer(raw_value: str, field_name: str) -> int:
    try:
        value = int(raw_value.strip())
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a whole number.") from exc

    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return value


def validate_budget(raw_value: str) -> str:
    text = raw_value.strip()
    if not text:
        return "none"

    try:
        budget_value = float(text)
    except ValueError as exc:
        raise ValueError("Budget must be a valid number.") from exc

    if budget_value <= 0:
        raise ValueError("Budget must be greater than zero.")

    return str(budget_value)


def build_prolog_service():
    from pyswip import Prolog

    prolog = Prolog()
    prolog.consult(str(KNOWLEDGE_BASE_PATH))
    return prolog


def query_estimate(prolog: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    query = (
        "estimate("
        f"{inputs['bedrooms']},"
        f"{inputs['floors']},"
        f"{inputs['finish']},"
        f"{inputs['location']},"
        f"{inputs['roof_type']},"
        f"{inputs['budget']},"
        "R)"
    )

    results = list(prolog.query(query))
    if not results:
        raise RuntimeError("No result returned from Prolog.")

    return parse_result(results[0]["R"])


def generate_and_save_estimate(prolog: Any, inputs: dict[str, Any]) -> tuple[dict[str, Any], int | None]:
    parsed = query_estimate(prolog, inputs)
    estimate_id = save_estimate(inputs, parsed)
    return parsed, estimate_id
