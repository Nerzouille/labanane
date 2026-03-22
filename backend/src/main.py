from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.workflow import router as workflow_router
from src.routes.export import router as export_router

app = FastAPI(title="Guided Analysis Workflow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflow_router)
app.include_router(export_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
