from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import engine, Base
from src.routes.stream import router as stream_router
from src.routes.export import router as export_router

# Create database tables at startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Market Intelligence AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stream_router)
app.include_router(export_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
