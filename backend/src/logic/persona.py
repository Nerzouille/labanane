"""Business logic — LLM-powered persona generation.

Pure async functions. No workflow state, no WebSocket access.
"""
from __future__ import annotations
import ast
import json

from OpenHosta import emulate_async

from src.models.report import Persona, PersonaSet


def _coerce_to_list(value: object) -> list:
    """Coerce emulate_async() output to list.

    OpenHosta may return a JSON string instead of an actual list.
    """
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        try:
            parsed = ast.literal_eval(stripped)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, SyntaxError):
            pass
    return []


def _normalize_persona_list(raw: list) -> list[dict]:
    """Ensure exactly 3 persona dicts, each with required fields.

    - Coerces non-dict items to dicts where possible.
    - Fills missing fields with safe defaults.
    - Trims to 3 if more returned, pads with placeholder if fewer.
    """
    normalised: list[dict] = []
    for item in raw:
        if isinstance(item, dict):
            normalised.append(item)
        elif isinstance(item, str):
            # LLM occasionally returns a string description instead of a dict
            normalised.append({"name": item})

    # Fill missing fields with safe defaults
    result: list[dict] = []
    for p in normalised:
        result.append({
            "name": p.get("name") or "Unknown",
            "age_range": p.get("age_range") or "N/A",
            "occupation": p.get("occupation") or "N/A",
            "motivations": p.get("motivations") if isinstance(p.get("motivations"), list) else [],
            "pain_points": p.get("pain_points") if isinstance(p.get("pain_points"), list) else [],
        })

    # Trim to 3 if more returned
    result = result[:3]

    # Pad to 3 if fewer returned
    placeholder = {
        "name": "Unknown",
        "age_range": "N/A",
        "occupation": "N/A",
        "motivations": [],
        "pain_points": [],
    }
    while len(result) < 3:
        result.append(dict(placeholder))

    return result


async def generate_personas(
    product_description: str,
    products: list[dict],
    ai_analysis: dict,
) -> PersonaSet:
    """
    Generate exactly 3 distinct buyer personas for the described product.
    Each persona should target a meaningfully different buyer profile (age, use case, or motivation).
    Use the product list (titles, prices, features) and the market analysis (viability score,
    key risks, key opportunities, target segment) to ground the personas in real data.

    Return a JSON array of exactly 3 objects. Each object must have:
      - name: string (archetype label, e.g. "The Weekend Creator")
      - age_range: string (e.g. "25-35")
      - occupation: string (e.g. "Freelance graphic designer")
      - motivations: array of 2-3 short strings describing what drives this persona to buy
      - pain_points: array of 2-3 short strings describing frustrations this persona has

    Do not return fewer or more than 3 objects. Do not include explanations, only the array.
    """
    result = await emulate_async()
    raw = _coerce_to_list(result)
    normalised = _normalize_persona_list(raw)
    return PersonaSet.model_validate({"personas": normalised})
