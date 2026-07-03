def calculate_rule_based_score(
    preferred_location: str,
    budget_min: float,
    budget_max: float,
    listing_location: str,
    rent: float,
) -> tuple[int, str]:
    reasons = []

    # --- Budget scoring (max 50 points) ---
    if budget_min <= rent <= budget_max:
        budget_score = 50
        reasons.append(f"Rent ₹{rent} fits comfortably within budget (₹{budget_min}-₹{budget_max})")
    elif rent > budget_max:
        overage_pct = (rent - budget_max) / budget_max
        budget_score = max(0, 50 - int(overage_pct * 100))
        reasons.append(f"Rent ₹{rent} exceeds max budget of ₹{budget_max}")
    else:  # rent < budget_min
        budget_score = 40
        reasons.append(f"Rent ₹{rent} is below minimum budget of ₹{budget_min}, unusually cheap")

    # --- Location scoring (max 50 points) ---
    if preferred_location.strip().lower() in listing_location.strip().lower():
        location_score = 50
        reasons.append(f"Location '{listing_location}' matches preferred area '{preferred_location}'")
    else:
        location_score = 0
        reasons.append(f"Location '{listing_location}' does not match preferred area '{preferred_location}'")

    total_score = budget_score + location_score
    explanation = ". ".join(reasons) + "."

    return total_score, explanation