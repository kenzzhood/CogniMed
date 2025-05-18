from sqlalchemy.orm import Session
from app.db.db_schema import Priscription
from app.db.base import get_db


def add_priscription(
    doctor_name: str,
    visit_date: str,
    visit_time: str,
    hospital_name: str,
    username: str,
    file_url: str,
    db: Session = None,
):
    if db is None:
        db = next(get_db())
    priscription = Priscription(
        doctor_name=doctor_name,
        visit_date=visit_date,
        visit_time=visit_time,
        username=username,
        hospital_name=hospital_name,
        file_url=file_url,
    )
    db.add(priscription)
    db.commit()
    db.refresh(priscription)
    return priscription


def update_priscription(priscription_id: int, db: Session = None, **kwargs):
    if db is None:
        db = next(get_db())
    priscription = (
        db.query(Priscription).filter(Priscription.id == priscription_id).first()
    )
    if not priscription:
        return None
    for key, value in kwargs.items():
        if hasattr(priscription, key):
            setattr(priscription, key, value)
    db.commit()
    db.refresh(priscription)
    return priscription


def delete_priscription(priscription_id: int, db: Session = None):
    if db is None:
        db = next(get_db())
    priscription = (
        db.query(Priscription).filter(Priscription.id == priscription_id).first()
    )
    if not priscription:
        return False
    db.delete(priscription)
    db.commit()
    return True


def get_priscription(priscription_id: int, db: Session = None):
    if db is None:
        db = next(get_db())
    priscription = (
        db.query(Priscription).filter(Priscription.id == priscription_id).first()
    )
    return priscription


def get_user_priscriptions(username: str, db: Session = None):
    if db is None:
        db = next(get_db())
    priscriptions = (
        db.query(Priscription).filter(Priscription.username == username).all()
    )
    return priscriptions
