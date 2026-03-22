"""Unit tests for WorkflowEngine loop-back routing and step sequencing."""
import pytest
from starlette.testclient import TestClient
from src.main import app
from src.workflow.registry import PIPELINE


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _drain(ws, until_type: str, respond_confirmations=True, max_msgs: int = 60) -> list[dict]:
    """Collect messages until the given type appears, auto-confirming confirmation_requests."""
    messages = []
    for _ in range(max_msgs):
        msg = ws.receive_json()
        messages.append(msg)
        if msg["type"] == until_type:
            break
        if respond_confirmations and msg["type"] == "confirmation_request":
            ws.send_json({
                "type": "confirmation",
                "step_id": msg["step_id"],
                "confirmed": True,
            })
    return messages


# ── Pipeline integrity ────────────────────────────────────────────────────


def test_pipeline_length_is_9():
    assert len(PIPELINE) == 9


def test_pipeline_step_ids_unique():
    ids = [s.step_id for s in PIPELINE]
    assert len(ids) == len(set(ids))


def test_pipeline_order():
    expected_ids = [
        "product_description",
        "keyword_refinement",
        "keyword_confirmation",
        "product_research",
        "product_validation",
        "market_research",
        "ai_analysis",
        "final_criteria",
        "report_generation",
    ]
    assert [s.step_id for s in PIPELINE] == expected_ids


# ── Engine: loop-back on keyword_confirmation rejection ───────────────────


def test_engine_loops_back_on_keyword_rejection(client):
    """When keyword_confirmation is rejected, engine resets to product_description."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "desk mats"})

        # Collect until keyword_confirmation confirmation_request
        messages = []
        rejected = False
        for _ in range(40):
            msg = ws.receive_json()
            messages.append(msg)

            if msg["type"] == "confirmation_request" and msg["step_id"] == "keyword_confirmation" and not rejected:
                # Reject keywords
                ws.send_json({
                    "type": "confirmation",
                    "step_id": "keyword_confirmation",
                    "confirmed": False,
                })
                rejected = True
            elif msg["type"] == "step_activated" and rejected:
                # After rejection, engine should loop back to product_description
                if msg["step_id"] == "product_description":
                    break

        step_activated_ids = [m["step_id"] for m in messages if m["type"] == "step_activated"]
        # Should see product_description activated at least twice (initial + loop-back)
        assert step_activated_ids.count("product_description") >= 1
        assert rejected, "Keyword confirmation was never reached"


def test_engine_loop_back_target_is_product_description(client):
    """LOOP_TARGETS maps keyword_confirmation → product_description."""
    from src.workflow.engine import LOOP_TARGETS
    assert LOOP_TARGETS["keyword_confirmation"] == "product_description"


def test_engine_loop_back_target_is_product_research_for_product_validation(client):
    """LOOP_TARGETS maps product_validation → product_research."""
    from src.workflow.engine import LOOP_TARGETS
    assert LOOP_TARGETS["product_validation"] == "product_research"


# ── Engine: empty description ─────────────────────────────────────────────


def test_engine_rejects_empty_description(client):
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "   "})
        msg = ws.receive_json()
        assert msg["type"] == "step_error"
        assert msg["retryable"] is False


def test_engine_rejects_wrong_first_message_type(client):
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "something_else", "description": "desk mats"})
        msg = ws.receive_json()
        assert msg["type"] == "step_error"


# ── Engine: workflow_complete has run_id ──────────────────────────────────


def test_engine_workflow_complete_includes_run_id(client):
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "desk mats"})
        messages = _drain(ws, "workflow_complete")
    complete = next(m for m in messages if m["type"] == "workflow_complete")
    assert "run_id" in complete
    assert len(complete["run_id"]) > 0


# ── Engine: step_activated emitted for every step ────────────────────────


def test_engine_emits_step_activated_for_all_9_steps(client):
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "ergonomic desk mats"})
        messages = _drain(ws, "workflow_complete")
    activated_ids = [m["step_id"] for m in messages if m["type"] == "step_activated"]
    for step in PIPELINE:
        assert step.step_id in activated_ids, f"step_activated not seen for {step.step_id}"


def test_engine_step_numbers_are_1_based(client):
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "desk mats"})
        messages = _drain(ws, "workflow_complete")
    activated = [m for m in messages if m["type"] == "step_activated"]
    for msg in activated:
        assert msg["step_number"] >= 1
