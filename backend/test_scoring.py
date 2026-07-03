from app.scoring import calculate_rule_based_score

# Test 1: Perfect match
score, explanation = calculate_rule_based_score(
    preferred_location="Koramangala",
    budget_min=10000,
    budget_max=18000,
    listing_location="Koramangala, Bangalore",
    rent=15000,
)
print("Test 1 (should score high):", score, "-", explanation)

# Test 2: Over budget
score, explanation = calculate_rule_based_score(
    preferred_location="Koramangala",
    budget_min=10000,
    budget_max=18000,
    listing_location="Koramangala, Bangalore",
    rent=25000,
)
print("Test 2 (over budget):", score, "-", explanation)

# Test 3: Wrong location
score, explanation = calculate_rule_based_score(
    preferred_location="Koramangala",
    budget_min=10000,
    budget_max=18000,
    listing_location="Delhi",
    rent=15000,
)
print("Test 3 (wrong location):", score, "-", explanation)

# Test 4: Both wrong
score, explanation = calculate_rule_based_score(
    preferred_location="Koramangala",
    budget_min=10000,
    budget_max=18000,
    listing_location="Delhi",
    rent=30000,
)
print("Test 4 (both wrong):", score, "-", explanation)