import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from config import settings
from models import SSEPayload, SSEErrorPayload

router = APIRouter()


async def event_generator():
    try:
        for i in range(settings.event_count):
            payload = SSEPayload(
                id=i,
                status="processing",
                percentage=(i + 1) * (100 / settings.event_count),
                message=f"Task {i + 1} of {settings.event_count} complete",
            )
            yield f"data: {payload.model_dump_json()}\n\n"
            await asyncio.sleep(settings.event_interval)
    except Exception as e:
        error = SSEErrorPayload(message=str(e))
        yield f"event: error\ndata: {error.model_dump_json()}\n\n"


@router.get("/stream")
async def stream():
    return StreamingResponse(event_generator(), media_type="text/event-stream")
