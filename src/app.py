from __future__ import annotations

from pyswip import Prolog


def prompt_int(label: str) -> int:
    while True:
        raw = input(label).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if value <= 0:
            print("Value must be greater than zero.")
            continue
        return value


def prompt_choice(label: str, options: list[str]) -> str:
    options_lower = [o.lower() for o in options]
    while True:
        raw = input(label).strip().lower()
        if raw in options_lower:
            return raw
        print(f"Please choose one of: {', '.join(options)}")


def prompt_budget(label: str) -> str:
    raw = input(label).strip()
    if not raw:
        return "none"
    try:
        value = float(raw)
    except ValueError:
        print("Invalid number. Budget ignored.")
        return "none"
    if value <= 0:
        print("Budget must be greater than zero. Ignored.")
        return "none"
    # Prolog expects a number literal, not quoted text
    return str(value)


def parse_result(result_atom: str) -> dict:
    # result(Area,materials(C,S,B,T),Base,Final,Feasibility,[Reasons])
    # We'll do minimal parsing to present a readable output.
    return {"raw": result_atom}


def main() -> None:
    print("Residential Construction Cost Estimator (Prolog)")

    bedrooms = prompt_int("Bedrooms: ")
    floors = prompt_int("Floors: ")
    finish = prompt_choice("Finish (basic/standard/luxury): ",
                           ["basic", "standard", "luxury"])
    location = prompt_choice("Location (rural/urban): ", ["rural", "urban"])
    budget = prompt_budget("Budget (optional, press Enter to skip): ")

    prolog = Prolog()
    prolog.consult("src/knowledge_base.pl")

    query = (
        "estimate("
        f"{bedrooms},"
        f"{floors},"
        f"{finish},"
        f"{location},"
        f"{budget},"
        "R)"
    )

    results = list(prolog.query(query))
    if not results:
        print("No result returned from Prolog.")
        return

    result = results[0]["R"]
    parsed = parse_result(result)

    print("\n--- ESTIMATION RESULT ---")
    print(parsed["raw"])


if __name__ == "__main__":
    main()
