# OpenHosta `emulate_async()` — Actual Runtime Behavior

## What it is

`emulate_async()` is OpenHosta's magic LLM-calling function. When called inside a function
whose return type is annotated, it sends the function's docstring + signature to the LLM and
returns a value that the LLM generated.

## The core problem: it returns strings, not Python objects

Despite the function having a return type annotation (e.g. `-> list[str]` or `-> dict`),
`emulate_async()` does **not** deserialize the LLM's response into that Python type.

Instead, it returns the raw LLM output as a **string** — specifically, the Python `repr()`
or JSON serialization of the intended value.

### Concrete examples

#### When the annotated return type is `list[str]`

```python
async def generate_search_queries(product_description: str) -> list[str]:
    return await emulate_async()
```

The LLM generates something like `["desk mat", "office mat", "wrist rest"]` and OpenHosta
returns it as the **string**:

```
"['desk mat', 'office mat', 'wrist rest']"
```

Note: it uses Python's `repr()` format (single quotes), **not** JSON (double quotes).
This means `json.loads()` alone fails. You need `ast.literal_eval()` as a fallback.

When the caller does `{#each keywords as kw}` in Svelte, it iterates the **characters** of
the string: `[`, `'`, `d`, `e`, `s`, `k`, ` `, `m`, `a`, `t`, `'`, `,` ...
Each character becomes its own badge/chip in the UI.

#### When the annotated return type is `dict` (or a Pydantic model)

```python
async def generate_market_analysis(...) -> MarketAnalysis:
    result_dict = await emulate_async()
    return MarketAnalysis.model_validate(result_dict)
```

The LLM generates a JSON object and OpenHosta returns it as the **string**:

```
'{\n  "viability_score": 74,\n  "go_no_go": "conditional",\n  ...\n}'
```

Pydantic's `model_validate()` expects a `dict`, not a `str`. It raises:

```
ValidationError: Input should be a valid dictionary or instance of MarketAnalysis
[type=model_type, input_value='{\n "viability_score"...}', input_type=str]
```

#### When the annotated return type is `list[dict]`

```python
async def parse_marketplace_data(cleaned_text: str) -> list[dict]:
    return await emulate_async()
```

Returns a string like `"[{'title': 'Product A', 'price': '9.99', ...}]"`.

When the caller tries to iterate and call `.get()` on each item:

```python
for p in items:
    key = p.get("url") or p.get("title")  # AttributeError: 'str' has no attribute 'get'
```

Each `p` is a **character** of the string. `.get()` on a `str` raises `AttributeError`,
which is silently swallowed by `asyncio.gather(return_exceptions=True)`, producing an empty
product list and a "No products found" error.

---

## Why it causes maximum confusion

### 1. Type annotations are lies

The function signature says `-> list[str]`. Python's type checker, your IDE, and your
intuition all say "this returns a list". But at runtime it returns a `str`. Static analysis
tools (`mypy`, `pyright`, `svelte-check`) cannot catch this — the lie is at the boundary
of a library call.

### 2. Failure modes are indirect and silent

| Return type | What OpenHosta returns | Observed symptom | Actual cause visibility |
|---|---|---|---|
| `list[str]` | `"['kw1', 'kw2']"` | 50 character-badges in the UI | Non-obvious |
| `list[dict]` | `"[{'title': ...}]"` | "No products found" error | Invisible — swallowed by `gather` |
| `dict` | `'{"key": "val"}'` | Pydantic `ValidationError` with raw string | Visible in error message |

### 3. Tests mock the problem away

The standard test pattern is:

```python
with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=["kw1", "kw2"])):
    result = await generate_search_queries("desk mats")
```

This makes the mock return a **real list** — the coercion code path (`isinstance(value, str)`)
is never hit. 188 tests pass. Production fails. The test suite provides false confidence
because it validates behaviour *with correct input* but never validates *handling of what
OpenHosta actually returns*.

### 4. The `repr()` vs JSON ambiguity

OpenHosta sometimes returns JSON (double-quoted), sometimes Python repr (single-quoted),
depending on how the model formatted its response. This means:

- `json.loads()` alone fails on `"['a', 'b']"` (single quotes are not valid JSON)
- `ast.literal_eval()` alone fails on `'{"key": null}'` (`null` is not valid Python)
- You need to try **both in sequence**

---

## The fix pattern

```python
import ast, json

def _coerce_to_str_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        stripped = value.strip()
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
        return [stripped]  # last resort: treat whole string as one item
    return []
```

Same pattern applies for `dict` (`_coerce_to_dict`) and `list[dict]` (`_coerce_to_list_of_dicts`).

**Critical rule:** always test coercion functions **directly** with string inputs, not only
through mocks that return proper Python objects. Example:

```python
def test_coerce_str_list_python_repr_string():
    # What OpenHosta actually returns: str(list)
    assert _coerce_to_str_list("['desk mat', 'office mat']") == ["desk mat", "office mat"]
```

---

## Second-level problem: LLM ignores nested model shapes

Even after coercing the outer string to a dict, the LLM often returns the **wrong value
shapes for nested fields**. Examples observed against `MarketAnalysis`:

| Field | Expected | LLM returned | Fix |
|---|---|---|---|
| `viability_score` | `int` (0–100) | `8.5` (float, often out of 10 not 100) | `round(float)` → `int` |
| `go_no_go` | `"go"` / `"no-go"` / `"conditional"` | `"Go"` (capitalised) | `.lower()` + canonical map |
| `criteria` | `[{"label": str, "score": int}]` | `["Customer demand", "Pricing"]` (list of strings) | wrap each string as `{"label": s, "score": 50}` |
| `target_persona` | `{"description": str}` | `"Health-conscious individuals..."` (plain string) | wrap as `{"description": s}` |
| `differentiation_angles` | `{"content": str}` | `["Eco-friendly", "Bundle offers"]` (list) | join list → `{"content": ", ".join(...)}` |
| `competitive_overview` | `{"content": str}` | `"Moderate competition..."` (plain string) | wrap as `{"content": s}` |
| `competitive_overview` | `{"content": str}` | `[{"title": "...", "price": "..."}]` (product list!) | extract titles → join → wrap |

This is handled by `_normalize_market_analysis_dict()` in `logic/analysis.py`, applied
**after** `_coerce_to_dict()` and **before** `model_validate()`.

---

## Affected functions in this codebase

| Function | File | Return type | Coercion applied |
|---|---|---|---|
| `generate_search_queries` | `backend/src/logic/analysis.py` | `list[str]` | `_coerce_to_str_list` |
| `generate_market_analysis` | `backend/src/logic/analysis.py` | `MarketAnalysis` | `_coerce_to_dict` → `model_validate` |
| `parse_marketplace_data` | `backend/src/logic/scraper.py` | `list[dict]` | `_coerce_to_list_of_dicts` |
