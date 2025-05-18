from app.db.base import get_db
from app.db.db_schema import Auth


def add_user_auth(username: str, hashed_password: str, is_doctor: int, db=None):
    if db is None:
        db = next(get_db())
    user_auth = Auth(
        username=username, hashed_password=hashed_password, is_doctor=is_doctor
    )
    db.add(user_auth)
    db.commit()
    db.refresh(user_auth)
    return user_auth


def get_auth(username: str, db=None):
    if db is None:
        db = next(get_db())
    return db.query(Auth).filter(Auth.username == username).first()
