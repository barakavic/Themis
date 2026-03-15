from __future__ import annotations

try:
    from .database import initialize_database
    from .prolog_service import (
        build_prolog_service,
        format_estimate_text,
        generate_and_save_estimate,
        validate_budget,
        validate_positive_integer,
    )
except ImportError:
    from database import initialize_database
    from prolog_service import (
        build_prolog_service,
        format_estimate_text,
        generate_and_save_estimate,
        validate_budget,
        validate_positive_integer,
    )


def prompt_choice(label: str, options: list[str]) -> str:
    options_lower = [option.lower() for option in options]
    while True:
        raw = input(label).strip().lower()
        if raw in options_lower:
            return raw
        print(f"Please choose one of: {', '.join(options)}")


def prompt_positive_integer(label: str, field_name: str) -> int:
    while True:
        raw = input(label).strip()
        try:
            return validate_positive_integer(raw, field_name)
        except ValueError as error:
            print(error)


def prompt_budget(label: str) -> str:
    while True:
        raw = input(label).strip()
        try:
            return validate_budget(raw)
        except ValueError as error:
            print(error)


def collect_inputs() -> dict[str, int | str]:
    return {
        "bedrooms": prompt_positive_integer("Bedrooms: ", "Bedrooms"),
        "floors": prompt_positive_integer("Floors: ", "Floors"),
        "finish": prompt_choice(
            "Finish (basic/standard/luxury): ",
            ["basic", "standard", "luxury"],
        ),
        "location": prompt_choice("Location (rural/urban): ", ["rural", "urban"]),
        "roof_type": prompt_choice(
            "Roof type (gable/hip/flat): ",
            ["gable", "hip", "flat"],
        ),
        "budget": prompt_budget("Budget (optional, press Enter to skip): "),
    }


def main() -> None:
    print("Residential Construction Cost Estimator (CLI)")
    initialize_database()
    prolog = build_prolog_service()
    inputs = collect_inputs()
    parsed, estimate_id = generate_and_save_estimate(prolog, inputs)
    print()
    print(format_estimate_text(parsed, estimate_id))


if __name__ == "__main__":
    main()
