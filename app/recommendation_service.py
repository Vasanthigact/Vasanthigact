from typing import Any, Dict
from urllib.parse import quote_plus

from .gemini_utils import (
    get_home_recommendations,
    get_party_recommendations,
    get_jewelry_recommendations,
)
from .schemas import (
    HomeBudgetInput,
    JewelryBudgetInput,
    PartyBudgetInput,
)


def add_shopping_links(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add India-friendly shopping/search links to AI recommendations.
    """

    recommendation_keys = [
        "home_recommendations",
        "party_recommendations",
        "jewelry_recommendations",
    ]

    for key in recommendation_keys:
        for item in result.get(key, []):
            search_terms = item.get(
                "search_terms",
                item.get("item_type", "")
            )

            query = quote_plus(str(search_terms))

            item["shopping_links"] = {
                "amazon": (
                    "https://www.amazon.in/s?k="
                    + query
                ),
                "flipkart": (
                    "https://www.flipkart.com/search?q="
                    + query
                ),
                "google": (
                    "https://www.google.com/search?q="
                    + query
                ),
            }

    return result


def get_home_budget_recommendations(
    budget_input: HomeBudgetInput
) -> Dict[str, Any]:

    result = get_home_recommendations(budget_input)

    return add_shopping_links(result)


def get_party_budget_recommendations(
    budget_input: PartyBudgetInput
) -> Dict[str, Any]:

    result = get_party_recommendations(budget_input)

    return add_shopping_links(result)


def get_jewelry_budget_recommendations(
    budget_input: JewelryBudgetInput,
    image_path: str | None = None
) -> Dict[str, Any]:

    result = get_jewelry_recommendations(
        budget_input,
        image_path
    )

    return add_shopping_links(result)