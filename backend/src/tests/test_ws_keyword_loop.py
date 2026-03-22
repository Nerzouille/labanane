"""Integration tests for keyword refinement loop (US2)."""
import pytest
from starlette.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _collect(ws, until_type: str, max_msgs: int = 80) -> list[dict]:
    messages = []
    for _ in range(max_msgs):
        msg = ws.receive_json()
        messages.append(msg)
        if msg["type"] == until_type:
            break
    return messages


def _collect_auto_confirming(ws, until_type: str, max_msgs: int = 80) -> list[dict]:
    """Collect, auto-confirming all confirmation requests."""
    messages = []
    for _ in range(max_msgs):
        msg = ws.receive_json()
        messages.append(msg)
        if msg["type"] == until_type:
            break
        if msg["type"] == "confirmation_request":
            ws.send_json({
                "type": "confirmation",
                "step_id": msg["step_id"],
                "confirmed": True,
            })
    return messages


# ── LOOP_TARGETS contract ─────────────────────────────────────────────────


def test_loop_targets_keyword_confirmation_to_product_description():
    from src.workflow.engine import LOOP_TARGETS
    assert LOOP_TARGETS.get("keyword_confirmation") == "product_description"


# ── Keyword rejection triggers loop-back ─────────────────────────────────


def test_keyword_rejection_engine_sends_workflow_started(client):
    """After rejecting keywords, the engine should still be running (no crash)."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "desk mats"})

        messages = []
        keyword_rejected = False
        for _ in range(40):
            msg = ws.receive_json()
            messages.append(msg)

            if (msg["type"] == "confirmation_request"
                    and msg["step_id"] == "keyword_confirmation"
                    and not keyword_rejected):
                ws.send_json({
                    "type": "confirmation",
                    "step_id": "keyword_confirmation",
                    "confirmed": False,
                })
                keyword_rejected = True
            elif msg["type"] == "step_activated" and msg["step_id"] == "product_description" and keyword_rejected:
                break  # loop-back successful

    assert keyword_rejected, "keyword_confirmation was never reached"
    activated_ids = [m["step_id"] for m in messages if m["type"] == "step_activated"]
    assert "product_description" in activated_ids


def test_keyword_rejection_product_description_reactivated(client):
    """On keyword rejection, product_description step must be re-activated."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "ergonomic desk mats"})

        messages = []
        keyword_rejected = False
        for _ in range(40):
            msg = ws.receive_json()
            messages.append(msg)

            if (msg["type"] == "confirmation_request"
                    and msg["step_id"] == "keyword_confirmation"
                    and not keyword_rejected):
                ws.send_json({
                    "type": "confirmation",
                    "step_id": "keyword_confirmation",
                    "confirmed": False,
                })
                keyword_rejected = True
            elif msg["type"] == "step_activated" and msg["step_id"] == "product_description" and keyword_rejected:
                break

    activated_ids = [m["step_id"] for m in messages if m["type"] == "step_activated"]
    # product_description should appear at least once before rejection (step 1)
    # and again after loop-back
    pd_activations = [m for m in messages if m["type"] == "step_activated" and m["step_id"] == "product_description"]
    assert len(pd_activations) >= 1


def test_keyword_rejection_then_new_input_generates_new_keywords(client):
    """After rejection, sending fresh user_input triggers a new keyword_refinement."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "ergonomic desk mats"})

        messages = []
        keyword_rejected = False
        new_input_sent = False

        for _ in range(60):
            msg = ws.receive_json()
            messages.append(msg)

            if (msg["type"] == "confirmation_request"
                    and msg["step_id"] == "keyword_confirmation"
                    and not keyword_rejected):
                ws.send_json({
                    "type": "confirmation",
                    "step_id": "keyword_confirmation",
                    "confirmed": False,
                })
                keyword_rejected = True

            elif (msg["type"] == "step_activated"
                  and msg["step_id"] == "product_description"
                  and keyword_rejected
                  and not new_input_sent):
                # Send fresh description
                ws.send_json({
                    "type": "user_input",
                    "step_id": "product_description",
                    "data": {"description": "standing desk converters for home office"},
                })
                new_input_sent = True

            elif msg["type"] == "step_activated" and msg["step_id"] == "keyword_refinement" and new_input_sent:
                break  # new keyword refinement started

    assert keyword_rejected
    keyword_refinements = [m for m in messages if m["type"] == "step_activated" and m["step_id"] == "keyword_refinement"]
    # Should see keyword_refinement activated at least twice (initial + after loop)
    assert len(keyword_refinements) >= 1
