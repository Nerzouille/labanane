from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes.stream import router as stream_router

app = FastAPI(title="SSE Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(stream_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
