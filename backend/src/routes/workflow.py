"""WebSocket route: ws://localhost:8000/ws/workflow

Direct browser→FastAPI connection (no SvelteKit BFF).
"""
from __future__ import annotations
import asyncio
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.workflow.engine import WorkflowEngine
from src.workflow.registry import PIPELINE
from src.workflow.run import WorkflowRun
from src.workflow.messages import StepErrorMessage

router = APIRouter()

# In-memory run store (keyed by run_id, cleaned on disconnect)
_runs: dict[str, WorkflowRun] = {}


@router.websocket("/ws/workflow")
async def workflow_endpoint(ws: WebSocket) -> None:
    await ws.accept()

    run_id = str(uuid.uuid4())
    incoming: asyncio.Queue = asyncio.Queue()

    async def listen() -> None:
        """Forward incoming WS messages to the engine's queue."""
        try:
            while True:
                msg = await ws.receive_json()
                await incoming.put(msg)
        except WebSocketDisconnect:
            pass
        except Exception:
            pass

    # Wait for the initial 'start' message
    try:
        first_msg = await ws.receive_json()
    except WebSocketDisconnect:
        return

    if first_msg.get("type") != "start":
        await ws.send_json(
            StepErrorMessage(
                step_id="product_description",
                error="First message must be type 'start'.",
                retryable=False,
            ).model_dump()
        )
        await ws.close()
        return

    description = (first_msg.get("description") or "").strip()
    if not description:
        await ws.send_json(
            StepErrorMessage(
                step_id="product_description",
                error="Description cannot be empty.",
                retryable=False,
            ).model_dump()
        )
        await ws.close()
        return

    run = WorkflowRun(
        run_id=run_id,
        total_steps=len(PIPELINE),
        description=description,
    )
    _runs[run_id] = run

    listener_task = asyncio.create_task(listen())

    try:
        engine = WorkflowEngine(PIPELINE)
        await engine.run(run, ws, incoming)
    except WebSocketDisconnect:
        pass
    finally:
        listener_task.cancel()
        _runs.pop(run_id, None)
