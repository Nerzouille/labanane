"""Happy path integration test (TDD — partially RED).

The architecture tests (connection, message sequence) should be GREEN.
The content tests (actual keywords, products, etc.) will be RED until
real step implementations replace the stubs.

Run: uv run pytest src/tests/test_ws_happy_path.py -v
"""
import pytest
from starlette.testclient import TestClient
from src.main import app
from src.workflow.registry import PIPELINE


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _collect_messages_until(ws, target_type: str, max_msgs: int = 50) -> list[dict]:
    """Collect messages until target_type is seen or max_msgs is reached."""
    messages = []
    for _ in range(max_msgs):
        msg = ws.receive_json()
        messages.append(msg)
        if msg["type"] == target_type:
            break
        # Auto-respond to confirmation requests (yes)
        if msg["type"] == "confirmation_request":
            ws.send_json({
                "type": "confirmation",
                "step_id": msg["step_id"],
                "confirmed": True,
            })
    return messages


def test_full_run_emits_workflow_complete(client):
    """A full happy-path run must end with workflow_complete."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "ergonomic desk mats"})
        messages = _collect_messages_until(ws, "workflow_complete", max_msgs=100)
        types = [m["type"] for m in messages]
        assert "workflow_complete" in types, f"workflow_complete not received. Got: {types}"


def test_full_run_emits_step_activated_for_each_step(client):
    """step_activated must be emitted for each step 1 through 9."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "ergonomic desk mats"})
        messages = _collect_messages_until(ws, "workflow_complete", max_msgs=100)

    activated = [m for m in messages if m["type"] == "step_activated"]
    step_numbers = [m["step_number"] for m in activated]
    # Should see step numbers 1 through 9 (may repeat on loop-back, but at minimum once each)
    assert set(range(1, len(PIPELINE) + 1)).issubset(set(step_numbers)), (
        f"Not all steps activated. Got step numbers: {sorted(set(step_numbers))}"
    )


def test_full_run_step_numbers_in_order(client):
    """step_number in step_activated messages must be 1-based and match PIPELINE index."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "test product"})
        messages = _collect_messages_until(ws, "workflow_complete", max_msgs=100)

    activated = [m for m in messages if m["type"] == "step_activated"]
    # In happy path (no loop-back), step numbers must be 1,2,3,...,9
    numbers = [m["step_number"] for m in activated]
    assert numbers == list(range(1, len(PIPELINE) + 1))


def test_confirmation_request_at_step_3(client):
    """Step 3 (keyword_confirmation) must emit confirmation_request."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "bamboo skincare"})
        messages = _collect_messages_until(ws, "workflow_complete", max_msgs=100)

    confirmation_steps = [
        m["step_id"] for m in messages if m["type"] == "confirmation_request"
    ]
    assert "keyword_confirmation" in confirmation_steps


def test_confirmation_request_at_step_5(client):
    """Step 5 (product_validation) must emit confirmation_request."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "bamboo skincare"})
        messages = _collect_messages_until(ws, "workflow_complete", max_msgs=100)

    confirmation_steps = [
        m["step_id"] for m in messages if m["type"] == "confirmation_request"
    ]
    assert "product_validation" in confirmation_steps


def test_workflow_complete_has_run_id(client):
    """workflow_complete must include a non-empty run_id."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "standing desk converter"})
        messages = _collect_messages_until(ws, "workflow_complete", max_msgs=100)

    complete = next(m for m in messages if m["type"] == "workflow_complete")
    assert "run_id" in complete
    assert complete["run_id"] != ""


# ── RED tests: business logic (will fail until real steps implemented) ────


def test_keyword_refinement_returns_3_to_5_keywords(client):
    """[RED] keyword_refinement step must return 3-5 keywords from the description."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "ergonomic office chair"})
        messages = _collect_messages_until(ws, "workflow_complete", max_msgs=100)

    kw_result = next(
        (m for m in messages if m["type"] == "step_result" and m["step_id"] == "keyword_refinement"),
        None,
    )
    assert kw_result is not None, "keyword_refinement step_result not found"
    keywords = kw_result["data"].get("keywords", [])
    assert 3 <= len(keywords) <= 5, f"Expected 3-5 keywords, got {len(keywords)}: {keywords}"


def test_product_research_returns_real_products(client):
    """[RED] product_research must return real marketplace products (not stubs)."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "bamboo skincare"})
        messages = _collect_messages_until(ws, "workflow_complete", max_msgs=100)

    pr_result = next(
        (m for m in messages if m["type"] == "step_result" and m["step_id"] == "product_research"),
        None,
    )
    assert pr_result is not None
    products = pr_result["data"].get("products", [])
    # Real products should have real URLs (not example.com stubs)
    for p in products:
        assert "example.com" not in p.get("url", ""), f"Stub product URL found: {p['url']}"
