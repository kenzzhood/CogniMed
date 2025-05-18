from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Text of the post",
    )


class PostCreate(PostBase):
    parent_id: UUID | None = Field(
        None,
        title="Parent post id (for replies)",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    )


class Post(PostBase):
    post_id: UUID = Field(..., example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    created_time: datetime = Field(
        default=datetime.now(),
        title="Date and time when was posted",
        example="2025-03-25 07:58:56.550604",
    )
    parent_id: UUID | None = Field(
        None,
        title="Parent post id (for replies)",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    )
    user_id: UUID | None = Field(
        None,
        title="User id of the post owner",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    )
    doctor_id: UUID | None = Field(
        None,
        title="Doctor id of the post owner",
        example="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    )
    replies: list["Post"] = []

    class Config:
        from_attributes = True
