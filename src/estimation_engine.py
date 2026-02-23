
# Material Prices (Hardcoded for MVP)

MATERIAL_PRICES = {
    "cement": 750,      # price per bag
    "steel": 120,       # price per kg
    "bricks": 15,       # price per brick
    "timber": 45000     # price per m3
}

FINISH_MULTIPLIERS = {
    "basic": 1.00,
    "standard": 1.15,
    "luxury": 1.35
}

LOCATION_MULTIPLIERS = {
    "rural": 1.00,
    "urban": 1.20
}

# Area Calculation

def calculate_area(bedrooms, floors):
    avg_bedroom_size = 12
    scaling_factor = 2.5
    circulation_factor = 0.20

    bedroom_area = bedrooms * avg_bedroom_size
    functional_area = bedroom_area * scaling_factor
    total_area = functional_area * (1 + circulation_factor)
    total_area *= floors

    return total_area


# Material Estimation

def calculate_materials(total_area, floors):
    cement = total_area * 5
    steel = total_area * 35
    bricks = total_area * 60
    timber = total_area * 0.03

    explanation_log = []

    # Structural rule
    if floors > 1:
        steel *= 1.5
        explanation_log.append(
            "Multi-storey structure detected: steel quantity increased by 50%."
        )

    materials = {
        "cement": cement,
        "steel": steel,
        "bricks": bricks,
        "timber": timber
    }

    return materials, explanation_log


# Calculation

def calculate_cost(materials):
    total_cost = 0

    for material, quantity in materials.items():
        total_cost += quantity * MATERIAL_PRICES[material]

    return total_cost

#  Multipliers

def apply_multipliers(base_cost, finish, location, explanation_log):
    finish_multiplier = FINISH_MULTIPLIERS[finish]
    location_multiplier = LOCATION_MULTIPLIERS[location]

    if finish != "basic":
        explanation_log.append(
            f"Finish level '{finish}' applied: cost multiplier {finish_multiplier}."
        )

    if location == "urban":
        explanation_log.append(
            "Urban location detected: cost increased due to logistics."
        )

    final_cost = base_cost * finish_multiplier * location_multiplier

    return final_cost, explanation_log


# Feasibility Evaluation

def evaluate_feasibility(final_cost, budget, explanation_log):
    if budget is None:
        return "feasible", explanation_log

    if final_cost > budget:
        explanation_log.append("Projected cost exceeds declared budget.")
        return "not_feasible", explanation_log

    elif final_cost > budget * 0.9:
        explanation_log.append(
            "Projected cost is close to budget limit."
        )
        return "conditional", explanation_log

    else:
        return "feasible", explanation_log



# Main Execution (Test Case)

if __name__ == "__main__":

    # Sample Input
    bedrooms = 3
    floors = 2
    finish = "standard"
    location = "urban"
    budget = 8000000

    # Execution Pipeline
    total_area = calculate_area(bedrooms, floors)

    materials, explanation = calculate_materials(total_area, floors)

    base_cost = calculate_cost(materials)

    final_cost, explanation = apply_multipliers(
        base_cost, finish, location, explanation
    )

    feasibility, explanation = evaluate_feasibility(
        final_cost, budget, explanation
    )

    # Output
    print("\n--- ESTIMATION RESULT ---")
    print(f"Total Area: {total_area:.2f} m²")
    print("\nMaterial Breakdown:")
    for k, v in materials.items():
        print(f"{k.capitalize()}: {v:.2f}")

    print(f"\nFinal Estimated Cost: {final_cost:,.2f}")
    print(f"Feasibility Status: {feasibility}")

    print("\nExplanation:")
    for reason in explanation:
        print(f"- {reason}")