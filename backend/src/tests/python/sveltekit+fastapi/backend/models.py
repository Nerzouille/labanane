from typing import Literal
from pydantic import BaseModel, Field


class SSEPayload(BaseModel):
    id: int = Field(ge=0)
    status: Literal["processing", "done", "error"]
    percentage: float = Field(ge=0, le=100)
    message: str


class SSEErrorPayload(BaseModel):
    status: Literal["error"] = "error"
    message: str
