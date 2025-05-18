from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    patient_username: str | None = None


class ChatResponse(BaseModel):
    response: str
