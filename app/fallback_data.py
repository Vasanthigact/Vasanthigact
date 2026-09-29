HOME_FALLBACK = {
    "total_budget": 0,
    "home_recommendations": [
        {
            "item_type": "LED Lights",
            "description": "Energy-efficient LED lights for home interiors.",
            "style": "Modern",
            "estimated_price": 1200,
            "search_terms": "LED home interior lights"
        },
        {
            "item_type": "Ceiling Fan",
            "description": "Energy-efficient ceiling fan for everyday use.",
            "style": "Modern",
            "estimated_price": 2500,
            "search_terms": "energy efficient ceiling fan"
        },
        {
            "item_type": "Furniture",
            "description": "Simple and functional furniture suitable for a modern home.",
            "style": "Minimal",
            "estimated_price": 5000,
            "search_terms": "modern home furniture"
        }
    ],
    "remaining_budget": 0,
    "styling_tips": [
        "Prefer products that match the existing room colors.",
        "Compare prices across multiple shopping platforms.",
        "Keep essential purchases within the planned budget."
    ]
}


PARTY_FALLBACK = {
    "total_budget": 0,
    "party_recommendations": [
        {
            "item_type": "Decoration",
            "description": "Basic decorations suitable for a small celebration.",
            "estimated_price": 1500,
            "search_terms": "party decoration items"
        },
        {
            "item_type": "Food",
            "description": "Budget-friendly food options for party guests.",
            "estimated_price": 3000,
            "search_terms": "party food catering"
        },
        {
            "item_type": "Venue",
            "description": "A simple venue option suitable for a small gathering.",
            "estimated_price": 5000,
            "search_terms": "party venue near me"
        }
    ],
    "remaining_budget": 0,
    "styling_tips": [
        "Plan the guest count before finalizing food quantities.",
        "Reserve part of the budget for unexpected expenses.",
        "Compare venue and decoration prices before booking."
    ]
}


JEWELRY_FALLBACK = {
    "total_budget": 0,
    "jewelry_recommendations": [
        {
            "item_type": "Earrings",
            "description": "Elegant earrings suitable for the selected occasion.",
            "style": "Classic",
            "estimated_price": 1500,
            "search_terms": "women elegant earrings"
        },
        {
            "item_type": "Necklace",
            "description": "A simple necklace that can complement a variety of outfits.",
            "style": "Minimal",
            "estimated_price": 2500,
            "search_terms": "minimal necklace"
        },
        {
            "item_type": "Bangle",
            "description": "Classic bangles suitable for traditional and festive outfits.",
            "style": "Traditional",
            "estimated_price": 1200,
            "search_terms": "traditional bangles"
        }
    ],
    "remaining_budget": 0,
    "styling_tips": [
        "Choose jewelry that complements the outfit rather than overpowering it.",
        "Consider the occasion before selecting the jewelry style.",
        "Compare prices before purchasing."
    ]
}


def get_home_fallback(budget: float) -> dict:
    result = HOME_FALLBACK.copy()
    result["total_budget"] = budget

    total = sum(
        item["estimated_price"]
        for item in result["home_recommendations"]
    )

    result["remaining_budget"] = max(
        budget - total,
        0
    )

    return result


def get_party_fallback(budget: float) -> dict:
    result = PARTY_FALLBACK.copy()
    result["total_budget"] = budget

    total = sum(
        item["estimated_price"]
        for item in result["party_recommendations"]
    )

    result["remaining_budget"] = max(
        budget - total,
        0
    )

    return result


def get_jewelry_fallback(budget: float) -> dict:
    result = JEWELRY_FALLBACK.copy()
    result["total_budget"] = budget

    total = sum(
        item["estimated_price"]
        for item in result["jewelry_recommendations"]
    )

    result["remaining_budget"] = max(
        budget - total,
        0
    )

    return result
    