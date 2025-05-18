from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.db_schema import User, Doctor
from app.schema.user import UserModel, DoctorModel

# from app.schema.auth import RegisterUserRequest
from app.utils.auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/u/{username}")
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/u/{username}")
def delete_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}


@router.get(
    path="/me",
    response_model=UserModel | DoctorModel,
    status_code=status.HTTP_200_OK,
    summary="Get current logged in user",
)
async def me(current_user: User | Doctor = Depends(get_current_user)) -> User | Doctor:
    """
    # Get information of the current logged in user:

    # Returns:
    - **current_user**: User -> The current logged in user information

    # Raises:
    - **HTTP 401**: User is not authenticated
    - **HTTP 401**: Could not validate credentials
    - **HTTP 422**: Validation error
    """
    return current_user
