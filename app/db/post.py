from datetime import datetime
from typing import List
import uuid
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.db.db_schema import Post as PostModel
from app.schema.post import PostCreate, Post


def post_msg(
    db: Session, post: PostCreate, user_or_doctor_id: UUID, doctor: bool = False
) -> PostModel:
    db_post: PostModel = PostModel(
        post_id=str(uuid.uuid4()),
        user_id=str(user_or_doctor_id) if not doctor else None,
        doctor_id=str(user_or_doctor_id) if doctor else None,
        text=post.text,
        created_time=datetime.now(),
        parent_id=str(post.parent_id) if post.parent_id else None,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_posts(db: Session, skip: int = 0, limit: int = 100) -> List[PostModel]:
    posts = (
        db.query(PostModel)
        .options(joinedload(PostModel.replies))
        .filter(PostModel.parent_id == None)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return posts


def get_post(db: Session, post_id: str) -> PostModel:
    post = (
        db.query(PostModel)
        .options(joinedload(PostModel.replies))
        .filter(PostModel.post_id == post_id)
        .first()
    )
    return post


def delete_post(db: Session, post_id: str) -> PostModel:
    post = db.query(PostModel).get(post_id)
    if post:
        db.delete(post)
        db.commit()
    return post
