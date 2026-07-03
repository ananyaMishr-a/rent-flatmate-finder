from app.scoring import calculate_llm_score

score, explanation, source = calculate_llm_score(
    preferred_location="Koramangala",
    budget_min=10000,
    budget_max=18000,
    listing_location="Koramangala, Bangalore",
    rent=15000,
    room_type="1BHK",
    furnishing_status="semi-furnished",
)

print("Score:", score)
print("Explanation:", explanation)
print("Source:", source)