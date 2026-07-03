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

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key) if api_key and api_key != "your-anthropic-api-key-here" else None


def calculate_llm_score(
    preferred_location: str,
    budget_min: float,
    budget_max: float,
    listing_location: str,
    rent: float,
    room_type: str,
    furnishing_status: str,
) -> tuple[int, str, str]:
    """
    Returns (score, explanation, source) where source is 'llm' or 'rule_based'.
    Falls back to rule-based scoring if the LLM call fails or is unavailable.
    """
    if client is None:
        score, explanation = calculate_rule_based_score(
            preferred_location, budget_min, budget_max, listing_location, rent
        )
        return score, explanation, "rule_based"

    prompt = f"""Given this room listing: location={listing_location}, rent=₹{rent}/month, room_type={room_type}, furnishing={furnishing_status}
And this tenant profile: preferred_location={preferred_location}, budget_range=₹{budget_min}-₹{budget_max}/month

Compute a compatibility score from 0 to 100 based on budget and location match.
Return ONLY valid JSON in this exact format, nothing else: {{"score": <number>, "explanation": "<brief string>"}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = response.content[0].text.strip()
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(raw_text)
        score = int(parsed["score"])
        explanation = str(parsed["explanation"])

        if not (0 <= score <= 100):
            raise ValueError("Score out of range")

        return score, explanation, "llm"

    except Exception as e:
        score, explanation = calculate_rule_based_score(
            preferred_location, budget_min, budget_max, listing_location, rent
        )
        return score, f"{explanation} (LLM unavailable: fell back to rule-based scoring)", "rule_based"