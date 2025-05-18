import jwt
import datetime as dt
from datetime import timedelta
from app.settings import settings
from app.utils.security import verify_password_hash
from app.db.user import get_user
from app.db.doctor import get_doctor
from app.db.auth import get_auth
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.schema.auth import TokenData
from fastapi.security import OAuth2PasswordBearer
from app.db.base import get_db
from uuid import UUID


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = dt.datetime.now(dt.timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(username: str, password: str, doctor=False, db=None):
    auth = get_auth(username, db)
    if auth and verify_password_hash(password, auth.hashed_password):
        return get_user(username, db) if not doctor else get_doctor(username, db)
    return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        is_doctor: bool = payload.get("is_doctor")
        _id: UUID = payload.get("id")
        if username is None or is_doctor is None or _id is None:
            raise credentials_exception
        token_data = TokenData(username=username, is_doctor=is_doctor, id=_id)
    except jwt.PyJWTError:
        raise credentials_exception

    user = (
        get_doctor(username=username, db=db)
        if is_doctor
        else get_user(username=token_data.username, db=db)
    )
    if user is None:
        raise credentials_exception
    return user
