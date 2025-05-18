from app.db.base import get_db
from app.db.db_schema import User
from sqlalchemy.orm import Session
from pydantic import EmailStr


def add_user(
    email: EmailStr,
    username: str,
    name: str,
    phone: str,
    date_of_birth: str,
    gender: str,
    blood_group: str,
    relation_number: str,
    family_doctor_name: str,
    family_doctor_number: str,
    height: str,
    weight: str,
    aadhaar_number: str,
    db: Session = None,
):
    if db is None:
        db = next(get_db())
    user = User(
        email=email,
        username=username,
        name=name,
        phone=phone,
        date_of_birth=date_of_birth,
        gender=gender,
        blood_group=blood_group,
        relation_number=relation_number,
        family_doctor_name=family_doctor_name,
        family_doctor_number=family_doctor_number,
        height=height,
        weight=weight,
        aadhaar_number=aadhaar_number,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def is_user(username: str, db: Session = None):
    if db is None:
        db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    return user is not None


def get_user(username: str, db: Session = None):
    if db is None:
        db = next(get_db())
    return db.query(User).filter(User.username == username).first()


def update_user(username: str, email: str = None, name: str = None, db: Session = None):
    if db is None:
        db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if email:
        user.email = email
    if name:
        user.name = name
    db.commit()
    db.refresh(user)
    return user


def delete_user(username: str, db: Session = None):
    if db is None:
        db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def list_users(db: Session = None):
    if db is None:
        db = next(get_db())
    return db.query(User).all()
