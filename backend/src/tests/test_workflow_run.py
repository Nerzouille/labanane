"""Unit tests for WorkflowRun.get_output() and status transitions."""
from src.workflow.run import WorkflowRun, StepOutput, WorkflowStatus
from src.tests.conftest import make_run


# ── get_output ────────────────────────────────────────────────────────────


def test_get_output_returns_empty_dict_for_missing_step():
    run = make_run()
    assert run.get_output("nonexistent_step") == {}


def test_get_output_returns_data_for_confirmed_step():
    run = make_run(confirmed_outputs={"keyword_confirmation": {"keywords": ["mat", "pad"]}})
    assert run.get_output("keyword_confirmation") == {"keywords": ["mat", "pad"]}


def test_get_output_returns_empty_dict_not_raises_for_optional_step():
    run = make_run()
    # Should never raise — safe for optional upstream reads
    result = run.get_output("market_research")
    assert isinstance(result, dict)


def test_get_output_does_not_expose_confirmed_outputs_directly():
    """Steps must use get_output(), not confirmed_outputs."""
    run = make_run(confirmed_outputs={"kw": {"keywords": ["a"]}})
    # Ensure get_output returns the data dict, not the StepOutput wrapper
    result = run.get_output("kw")
    assert isinstance(result, dict)
    assert "keywords" in result
    # It must NOT be a StepOutput object
    assert not hasattr(result, "step_id")


def test_get_output_returns_correct_data_for_multiple_steps():
    run = make_run(
        confirmed_outputs={
            "step_a": {"foo": 1},
            "step_b": {"bar": 2},
        }
    )
    assert run.get_output("step_a") == {"foo": 1}
    assert run.get_output("step_b") == {"bar": 2}
    assert run.get_output("step_c") == {}


# ── WorkflowStatus values ─────────────────────────────────────────────────


def test_workflow_status_has_required_values():
    assert WorkflowStatus.idle
    assert WorkflowStatus.running
    assert WorkflowStatus.awaiting_confirmation
    assert WorkflowStatus.complete
    assert WorkflowStatus.error


def test_workflow_run_default_status_is_idle():
    run = WorkflowRun(run_id="x", total_steps=9)
    assert run.status == WorkflowStatus.idle


def test_workflow_run_default_current_step_is_zero():
    run = WorkflowRun(run_id="x", total_steps=9)
    assert run.current_step_index == 0


def test_workflow_run_has_run_id():
    run = WorkflowRun(run_id="abc-123", total_steps=9)
    assert run.run_id == "abc-123"


def test_step_output_default_confirmed_is_true():
    so = StepOutput(step_id="s01", data={"foo": "bar"})
    assert so.confirmed is True
