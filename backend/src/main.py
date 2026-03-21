from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routes.stream import router as stream_router
from src.routes.export import router as export_router
from src.routes.workflow import router as workflow_router

app = FastAPI(title="Market Intelligence AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stream_router)
app.include_router(export_router)
app.include_router(workflow_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
