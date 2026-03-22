"""WebSocket contract tests (TDD).

Architecture tests that should be GREEN:
- connection accepted
- workflow_started sent after start
- step_activated for each step
- total_steps derived from PIPELINE length

Business logic tests will be RED until steps are implemented.

Run: uv run pytest src/tests/test_ws_contract.py -v
"""
import pytest
from starlette.testclient import TestClient
from src.main import app
from src.workflow.registry import PIPELINE


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ── Architecture: connection & message shape ──────────────────────────────


def test_ws_connection_accepted(client):
    """WebSocket connection at /ws/workflow must be accepted."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "ergonomic desk mats"})
        msg = ws.receive_json()
        assert msg["type"] == "workflow_started"


def test_workflow_started_total_steps(client):
    """workflow_started must report total_steps equal to len(PIPELINE)."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "test"})
        msg = ws.receive_json()
        assert msg["total_steps"] == len(PIPELINE)


def test_workflow_started_step_ids(client):
    """workflow_started must list step_ids for all pipeline steps."""
    expected = [s.step_id for s in PIPELINE]
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "test"})
        msg = ws.receive_json()
        assert msg["step_ids"] == expected


def test_step_activated_sent_for_first_step(client):
    """step_activated must be sent immediately after workflow_started."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "test"})
        ws.receive_json()  # workflow_started
        msg = ws.receive_json()
        assert msg["type"] == "step_activated"
        assert msg["step_id"] == PIPELINE[0].step_id
        assert msg["step_number"] == 1


def test_step_activated_has_required_fields(client):
    """step_activated must include step_id, step_number, total_steps, label."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "test"})
        ws.receive_json()  # workflow_started
        msg = ws.receive_json()  # step_activated
        assert "step_id" in msg
        assert "step_number" in msg
        assert "total_steps" in msg
        assert "label" in msg


# ── Input validation ──────────────────────────────────────────────────────


def test_empty_description_returns_step_error(client):
    """Empty description must trigger step_error (not crash)."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "start", "description": "   "})
        msg = ws.receive_json()
        assert msg["type"] == "step_error"
        assert msg["retryable"] is False


def test_wrong_first_message_type_returns_step_error(client):
    """Non-start first message must return step_error."""
    with client.websocket_connect("/ws/workflow") as ws:
        ws.send_json({"type": "confirmation", "step_id": "foo", "confirmed": True})
        msg = ws.receive_json()
        assert msg["type"] == "step_error"
        assert msg["retryable"] is False


# ── Pipeline integrity ────────────────────────────────────────────────────



def test_pipeline_step_ids_are_unique():
    """All step_ids in PIPELINE must be unique."""
    ids = [s.step_id for s in PIPELINE]
    assert len(ids) == len(set(ids))


def test_pipeline_step_ids_are_strings():
    """All step_ids must be non-empty strings."""
    for step in PIPELINE:
        assert isinstance(step.step_id, str)
        assert step.step_id != ""


def test_pipeline_component_types_are_strings():
    """All component_type values must be non-empty strings."""
    for step in PIPELINE:
        assert isinstance(step.component_type, str)
        assert step.component_type != ""
