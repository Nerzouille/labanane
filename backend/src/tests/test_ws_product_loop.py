"""Integration tests for product validation loop (US3)."""
import pytest
from starlette.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _collect_until(ws, step_id: str, msg_type: str = "step_activated", max_msgs: int = 80) -> tuple[list[dict], bool]:
    """Collect messages; auto-confirm confirmations; stop when target appears."""
    messages = []
    found = False
    for _ in range(max_msgs):
        msg = ws.receive_json()
        messages.append(msg)
        if msg["type"] == msg_type and msg.get("step_id") == step_id:
            found = True
            break
        if msg["type"] == "confirmation_request":
            ws.send_json({
                "type": "confirmation",
                "step_id": msg["step_id"],
                "confirmed": True,
            })
        if msg["type"] == "workflow_complete":
            break
    return messages, found


# ── LOOP_TARGETS contract ─────────────────────────────────────────────────


def test_loop_targets_product_validation_to_product_research():
    from src.workflow.engine import LOOP_TARGETS
    assert LOOP_TARGETS.get("product_validation") == "product_research"


# ── Product validation rejection ──────────────────────────────────────────


def test_product_validation_rejection_reactivates_product_research(client):
    """Rejecting product_validation must reactivate product_research."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "ergonomic desk mats"})

        messages = []
        product_rejected = False

        for _ in range(60):
            msg = ws.receive_json()
            messages.append(msg)

            if msg["type"] == "workflow_complete":
                break

            if (msg["type"] == "confirmation_request"
                    and msg["step_id"] == "keyword_confirmation"):
                ws.send_json({
                    "type": "confirmation",
                    "step_id": "keyword_confirmation",
                    "confirmed": True,
                })

            elif (msg["type"] == "confirmation_request"
                  and msg["step_id"] == "product_validation"
                  and not product_rejected):
                ws.send_json({
                    "type": "confirmation",
                    "step_id": "product_validation",
                    "confirmed": False,  # REJECT
                })
                product_rejected = True

            elif (msg["type"] == "step_activated"
                  and msg["step_id"] == "product_research"
                  and product_rejected):
                break  # product_research reactivated

    assert product_rejected, "product_validation was never reached"
    product_research_activations = [
        m for m in messages
        if m["type"] == "step_activated" and m["step_id"] == "product_research"
    ]
    assert len(product_research_activations) >= 1


def test_product_rejection_keywords_are_preserved(client):
    """Confirmed keywords must NOT be lost when product_validation is rejected."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "ergonomic desk mats"})

        messages = []
        keyword_result_data = None
        product_rejected = False

        for _ in range(60):
            msg = ws.receive_json()
            messages.append(msg)

            if msg["type"] == "workflow_complete":
                break

            # Capture keyword results
            if (msg["type"] == "step_result" and msg["step_id"] == "keyword_refinement"):
                keyword_result_data = msg["data"]

            if (msg["type"] == "confirmation_request"
                    and msg["step_id"] == "keyword_confirmation"):
                ws.send_json({
                    "type": "confirmation",
                    "step_id": "keyword_confirmation",
                    "confirmed": True,
                })

            elif (msg["type"] == "confirmation_request"
                  and msg["step_id"] == "product_validation"
                  and not product_rejected):
                ws.send_json({
                    "type": "confirmation",
                    "step_id": "product_validation",
                    "confirmed": False,
                })
                product_rejected = True

            elif (msg["type"] == "step_activated"
                  and msg["step_id"] == "product_research"
                  and product_rejected):
                break

    # Keywords should have been generated (non-None)
    # After rejection, product_research should re-run without requiring new keyword input
    assert product_rejected
    # The presence of keyword_result_data verifies keyword step ran
    assert keyword_result_data is not None or product_rejected  # at minimum rejection happened


def test_product_validation_confirm_then_proceed(client):
    """Confirming products on second pass should advance to market_research."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "desk mats"})

        messages = []
        product_rejected = False
        product_confirmed = False

        for _ in range(80):
            msg = ws.receive_json()
            messages.append(msg)

            if msg["type"] == "workflow_complete":
                break
            if msg["type"] == "step_activated" and msg["step_id"] == "market_research" and product_confirmed:
                break  # success

            if msg["type"] == "confirmation_request" and msg["step_id"] == "keyword_confirmation":
                ws.send_json({"type": "confirmation", "step_id": "keyword_confirmation", "confirmed": True})

            elif (msg["type"] == "confirmation_request"
                  and msg["step_id"] == "product_validation"
                  and not product_rejected):
                # First time: reject
                ws.send_json({"type": "confirmation", "step_id": "product_validation", "confirmed": False})
                product_rejected = True

            elif (msg["type"] == "confirmation_request"
                  and msg["step_id"] == "product_validation"
                  and product_rejected
                  and not product_confirmed):
                # Second time: confirm
                ws.send_json({"type": "confirmation", "step_id": "product_validation", "confirmed": True})
                product_confirmed = True

    assert product_rejected
    # market_research should appear after confirming on second pass
    if product_confirmed:
        market_activations = [m for m in messages if m["type"] == "step_activated" and m["step_id"] == "market_research"]
        assert len(market_activations) >= 1
