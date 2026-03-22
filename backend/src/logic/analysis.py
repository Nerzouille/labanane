"""Business logic — LLM-powered market analysis functions.

Pure async functions. No workflow state, no WebSocket access.
"""
from __future__ import annotations
import ast
import json

from OpenHosta import emulate_async

from src.models.report import MarketAnalysis


def _coerce_to_str_list(value: object) -> list[str]:
    """Coerce emulate_async() output to list[str].

    OpenHosta may return a string repr of a list instead of an actual list.
    """
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        stripped = value.strip()
        # Try JSON first (["a", "b"]), then Python literal (['a', 'b'])
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except (json.JSONDecodeError, ValueError):
            pass
        try:
            parsed = ast.literal_eval(stripped)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except (ValueError, SyntaxError):
            pass
        # Last resort: treat the whole string as one keyword
        return [stripped]
    return []


async def generate_search_queries(product_description: str) -> list[str]:
    """
    Generate exactly 3 marketplace search keyword strings for the given product description.
    Return a JSON array of exactly 3 short strings, each suitable for an Amazon or Google Shopping search.
    Example: ["ergonomic desk mat", "office desk pad", "large mouse pad"]
    Do not return more or fewer than 3 items. Do not include explanations, only the array.
    """
    result = await emulate_async()
    return _coerce_to_str_list(result)


def _normalize_market_analysis_dict(d: dict) -> dict:
    """Normalize a raw LLM-produced dict to match MarketAnalysis field shapes.

    The LLM often returns:
    - go_no_go as 'Go' / 'No-Go' / 'Conditional' (wrong case)
    - criteria as a list of strings instead of [{"label": str, "score": int}]
    - target_persona as a plain string instead of {"description": str}
    - differentiation_angles as a list or string instead of {"content": str}
    - competitive_overview as a plain string instead of {"content": str}
    """
    result = dict(d)

    # viability_score: float → int (LLM sometimes returns 8.5 instead of 85)
    vs = result.get("viability_score")
    if isinstance(vs, float):
        result["viability_score"] = round(vs)

    # go_no_go: normalise to lowercase and canonical spelling
    gng = str(result.get("go_no_go", "conditional")).lower().strip()
    if gng in ("no-go", "no go", "nogo"):
        gng = "no-go"
    elif gng == "go":
        gng = "go"
    else:
        gng = "conditional"
    result["go_no_go"] = gng

    # criteria: list[str] → list[{"label": str, "score": int}]
    raw_criteria = result.get("criteria", [])
    if isinstance(raw_criteria, list) and raw_criteria:
        normalised = []
        for item in raw_criteria:
            if isinstance(item, dict) and "label" in item:
                normalised.append(item)
            elif isinstance(item, str):
                normalised.append({"label": item, "score": 50})
        result["criteria"] = normalised

    # target_persona: str → {"description": str}
    tp = result.get("target_persona")
    if isinstance(tp, str):
        result["target_persona"] = {"description": tp}

    # differentiation_angles: str | list[str] → {"content": str}
    da = result.get("differentiation_angles")
    if isinstance(da, str):
        result["differentiation_angles"] = {"content": da}
    elif isinstance(da, list):
        result["differentiation_angles"] = {"content": ", ".join(str(x) for x in da)}

    # competitive_overview: str | list → {"content": str}
    co = result.get("competitive_overview")
    if isinstance(co, str):
        result["competitive_overview"] = {"content": co}
    elif isinstance(co, list):
        # LLM sometimes puts the product list here; summarise as titles
        titles = [item.get("title", str(item)) if isinstance(item, dict) else str(item) for item in co]
        result["competitive_overview"] = {"content": ", ".join(titles)}

    return result


def _coerce_to_dict(value: object) -> dict:
    """Coerce emulate_async() output to dict.

    OpenHosta may return a JSON string instead of an actual dict.
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        try:
            parsed = ast.literal_eval(stripped)
            if isinstance(parsed, dict):
                return parsed
        except (ValueError, SyntaxError):
            pass
    return {}


async def generate_market_analysis(
    product_description: str,
    products: list[dict],
    trends: dict,
) -> MarketAnalysis:
    """
    Analyse market viability using competitor products and trend data.
    Return a fully populated MarketAnalysis with ALL of the following fields:

    - viability_score: integer between 0 and 100 (NOT 0-10). 0 = not viable, 100 = excellent.
    - go_no_go: exactly one of the strings "go", "no-go", or "conditional" (lowercase, no other values).
    - summary: one sentence verdict.
    - analysis: 2-3 sentence market analysis.
    - key_risks: list of exactly 3 short strings describing risks.
    - key_opportunities: list of exactly 3 short strings describing opportunities.
    - criteria: list of 3 to 5 objects, each with keys "label" (string) and "score" (integer 0-100).
    - target_persona: object with key "description" (string describing the ideal customer).
    - differentiation_angles: object with key "content" (string describing how to differentiate).
    - competitive_overview: object with key "content" (string summarising the competitive landscape).
    """
    result_dict = await emulate_async()
    normalised = _normalize_market_analysis_dict(_coerce_to_dict(result_dict))
    return MarketAnalysis.model_validate(normalised)
