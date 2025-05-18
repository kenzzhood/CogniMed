from typing import List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.schema.post import Post, PostCreate
from app.db.db_schema import User, Doctor
from app.utils.auth import get_current_user
from app.db.base import get_db
from app.db.post import (
    delete_post as db_delete_post,
    get_post as db_get_post,
    get_posts as db_get_posts,
    post_msg as db_post_msg,
)
from app.utils.faiss_utils import update_faiss_index
from app.db.doctor import is_doctor

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post(
    path="/",
    response_model=Post,
    status_code=status.HTTP_201_CREATED,
    summary="Post a new message",
)
async def post_msg(
    post: PostCreate = Body(
        ...,
        examples={
            "normal": {
                "summary": "A message is posted",
                "description": "Post creation works correctly.",
                "value": {
                    "user_id": "22a16cfe-3e06-40bb-9043-2fa419262cf2",
                    "text": "This is a Post",
                },
            },
        },
    ),
    db: Session = Depends(get_db),
    current_user_or_doctor: User | Doctor = Depends(get_current_user),
) -> Post:
    """
    # Post a new message and save it to the database:

    # Parameters:
    -  ### Request Body parameter :
        - **post: PostCreate**: a PostCreate model with the following information:
            - **user_id: UserBase (required)** -> User's Id
            - **text: str (required)** -> Post's text

    # Returns:
    - **post** : The message that was post with all the information

    # Raises:
    - **HTTP 401**: User is not authenticated
    - **HTTP 422**: Validation error

    Post a new message or reply. If parent_id is provided, this is a reply.
    """
    _is_doctor = is_doctor(current_user_or_doctor.username, db)
    data = db_post_msg(
        db=db, post=post, user_or_doctor_id=current_user_or_doctor.id, doctor=_is_doctor
    )
    # Update FAISS index with new post
    update_faiss_index(
        data.text,
        metadata={
            "post_id": data.post_id,
            "user_id": data.user_id,
            "doctor_id": data.doctor_id,
        },
    )
    return data


@router.get(
    path="/",
    response_model=List[Post],
    status_code=status.HTTP_200_OK,
    summary="Get a list of posts",
)
async def get_posts(
    skip: int = Query(
        default=0,
        title="Skip",
        description="Numbers of posts to skip",
        ge=0,
        example=0,
    ),
    limit: int = Query(
        default=None,
        title="limit",
        description="Limit the numbers of posts returned",
        ge=0,
        example=5,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Post]:
    """
    # Get a list of posts:

    # Parameters:
    -  ### Query parameters :
        - **skip: int (optional)** -> Numbers of posts to skip
        - **limit: int (optional)** -> The limit the numbers of posts returned

    # Returns:
    - **list[Tweet]** : A list of posts

    # Raises:
    - **HTTP 401**: User is not authenticated
    - **HTTP 422**: Validation error
    """

    db_posts: List[Post] = db_get_posts(db, skip=skip, limit=limit)
    return db_posts


@router.get(
    path="/{post_id}",
    response_model=Post,
    status_code=status.HTTP_200_OK,
    summary="Get a Post",
)
async def get_post(
    post_id: UUID = Path(
        ...,
        title="Post's id",
        description="The id of the post to find. (required)",
        examples={
            "normal": {
                "summary": "Get a post",
                "description": "Get post works correctly.",
                "value": "cd5bf8d1-8e70-49b2-a4e5-6c6d37fdd266",
            },
        },
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Post:
    """
    # Get a single twepostet with the given post id:

    # Parameters:
    -  ### Request Path parameter :
        - **post_id: UUID (required)** -> post's Id

    # Returns:
    - **post** : The post that was found with it's information

    # Raises:
    - **HTTP 401**: User is not authenticated
    - **HTTP 401**: Post not found
    - **HTTP 422**: Validation error
    """

    db_post: Post = db_get_post(db, post_id=str(post_id))
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@router.delete(
    path="/{post_id}",
    response_model=Post,
    status_code=status.HTTP_200_OK,
    summary="Delete a post",
)
async def delete_post(
    post_id: UUID = Path(
        ...,
        title="Post's id",
        description="The id of the post to be deleted. (required)",
        examples={
            "normal": {
                "summary": "A post is deleted",
                "description": "post delete works correctly.",
                "value": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            },
        },
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Post:
    """
    # Deletes a post with the given post id:

    # Parameters:
    -  ### Request Path parameter :
        - **post_id: UUID (required)** -> post's Id

    # Returns:
    - **post** : The post that was deleted with it's information

    # Raises:
    - **HTTP 401**: User is not authenticated
    - **HTTP 404**: Post not found
    - **HTTP 422**: Validation error
    """
    db_post: Post = db_delete_post(db, str(post_id))
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post
