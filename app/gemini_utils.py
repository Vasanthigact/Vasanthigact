import json
import os
import re
from typing import Optional

import google.generativeai as genai

from .config import GOOGLE_API_KEY
from .schemas import (
    HomeBudgetInput,
    JewelryBudgetInput,
    PartyBudgetInput,
)


if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


def get_model():
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured in the .env file."
        )

    return genai.GenerativeModel(MODEL_NAME)


def extract_json(text: str) -> dict:
    """
    Extract JSON from Gemini's response.
    Handles responses wrapped in markdown code blocks.
    """

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned
    )

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(
            r"\{.*\}",
            cleaned,
            flags=re.DOTALL
        )

        if match:
            return json.loads(match.group(0))

        raise ValueError(
            "Gemini returned an invalid JSON response."
        )


def generate_with_gemini(prompt: str) -> dict:
    """
    Send a prompt to Gemini and convert the response to JSON.
    """

    model = get_model()

    response = model.generate_content(prompt)

    if not response or not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return extract_json(response.text)


def get_home_recommendations(
    budget_input: HomeBudgetInput
) -> dict:

    prompt = f"""
You are PocketSmart AI, an intelligent budget planner
for users in India.

Create practical home interior/product recommendations.

Budget:
₹{budget_input.total_budget}

Requirements:
- Lights: {budget_input.num_lights}
- Fans: {budget_input.num_fans}
- Furniture items: {budget_input.num_furniture}
- Dining tables: {budget_input.num_dining_tables}

User preferences:
{budget_input.preferences or "No specific preferences"}

Return ONLY valid JSON in this structure:

{{
    "total_budget": 0,
    "home_recommendations": [
        {{
            "item_type": "",
            "description": "",
            "style": "",
            "estimated_price": 0,
            "search_terms": ""
        }}
    ],
    "remaining_budget": 0,
    "styling_tips": []
}}

Rules:
- Keep prices in Indian Rupees.
- Stay within the total budget.
- Use realistic Indian shopping terms.
- Give useful recommendations.
- Do not invent product URLs.
"""

    return generate_with_gemini(prompt)


def get_party_recommendations(
    budget_input: PartyBudgetInput
) -> dict:

    prompt = f"""
You are PocketSmart AI, an intelligent party budget planner
for users in India.

Create practical recommendations for a party.

Budget:
₹{budget_input.total_budget}

Party type:
{budget_input.party_type}

Number of guests:
{budget_input.num_guests}

Preferences:
{budget_input.preferences or "No specific preferences"}

Return ONLY valid JSON in this structure:

{{
    "total_budget": 0,
    "party_recommendations": [
        {{
            "item_type": "",
            "description": "",
            "estimated_price": 0,
            "search_terms": ""
        }}
    ],
    "remaining_budget": 0,
    "styling_tips": []
}}

Rules:
- Keep prices in Indian Rupees.
- Stay within the total budget.
- Consider venue, food, decoration and basic party requirements.
- Use realistic Indian shopping/search terms.
"""

    return generate_with_gemini(prompt)


def get_jewelry_recommendations(
    budget_input: JewelryBudgetInput,
    image_path: Optional[str] = None
) -> dict:

    image_instruction = ""

    if image_path:
        image_instruction = f"""
An outfit image has been uploaded for this request.

Image path:
{image_path}

Use the available outfit information when suggesting
jewelry styles.
"""

    prompt = f"""
You are PocketSmart AI, an intelligent jewelry planner
for users in India.

Create jewelry recommendations based on the user's
budget, occasion and preferences.

Budget:
₹{budget_input.total_budget}

Occasion:
{budget_input.occasion}

Preferences:
{budget_input.preferences or "No specific preferences"}

{image_instruction}

Return ONLY valid JSON in this structure:

{{
    "total_budget": 0,
    "jewelry_recommendations": [
        {{
            "item_type": "",
            "description": "",
            "style": "",
            "estimated_price": 0,
            "search_terms": ""
        }}
    ],
    "remaining_budget": 0,
    "styling_tips": []
}}

Rules:
- Keep prices in Indian Rupees.
- Stay within the total budget.
- Consider the occasion.
- Give Indian-friendly jewelry search terms.
- If an outfit image is available, consider its colors
  and overall style.
"""

    return generate_with_gemini(prompt)