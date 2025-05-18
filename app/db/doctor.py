from app.db.base import get_db
from app.db.db_schema import Doctor
from sqlalchemy.orm import Session, joinedload
from pydantic import EmailStr


def add_doctor(
    email: EmailStr,
    username: str,
    name: str,
    phone: str,
    specialization: str,
    hospital_name: str,
    db: Session = None,
):
    if db is None:
        db = next(get_db())
    doctor = Doctor(
        email=email,
        username=username,
        name=name,
        phone=phone,
        specialization=specialization,
        hospital_name=hospital_name,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def is_doctor(username: str, db: Session = None):
    if db is None:
        db = next(get_db())
    doctor = db.query(Doctor).filter(Doctor.username == username).first()
    return doctor is not None


def get_doctor(username: str, db: Session = None):
    if db is None:
        db = next(get_db())
    return (
        db.query(Doctor)
        .options(joinedload(Doctor.posts))
        .filter(Doctor.username == username)
        .first()
    )


def update_doctor(
    username: str, email: str = None, name: str = None, db: Session = None
):
    if db is None:
        db = next(get_db())
    doctor = db.query(Doctor).filter(Doctor.username == username).first()
    if not doctor:
        return None
    if email:
        doctor.email = email
    if name:
        doctor.name = name
    db.commit()
    db.refresh(doctor)
    return doctor


def delete_doctor(username: str, db: Session = None):
    if db is None:
        db = next(get_db())
    doctor = db.query(Doctor).filter(Doctor.username == username).first()
    if not doctor:
        return False
    db.delete(doctor)
    db.commit()
    return True


def list_doctors(db: Session = None):
    if db is None:
        db = next(get_db())
    return db.query(Doctor).all()
