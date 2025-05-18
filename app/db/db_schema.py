from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.db.base import Base, engine
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import BLOB
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    date_of_birth = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    blood_group = Column(String, nullable=False)
    relation_number = Column(String, nullable=False)
    family_doctor_name = Column(String, nullable=False)
    family_doctor_number = Column(String, nullable=False)
    height = Column(String, nullable=False)
    weight = Column(String, nullable=False)
    aadhaar_number = Column(String, unique=True, index=True, nullable=False)
    posts = relationship("Post", back_populates="user")


class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    specialization = Column(String, nullable=False)
    hospital_name = Column(String, nullable=False)
    posts = relationship("Post", back_populates="doctor")


class Auth(Base):
    __tablename__ = "auth"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_doctor = Column(Integer, nullable=False)  # 1 for doctor, 0 for not doctor


class Priscription(Base):
    __tablename__ = "priscriptions"
    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String, nullable=False)
    visit_date = Column(String, nullable=False)
    visit_time = Column(String, nullable=False)
    hospital_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    file_url = Column(String, nullable=False)


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    doctor_id = Column(String, ForeignKey("doctors.id"), nullable=True)
    text = Column(String)
    created_time = Column(DateTime)
    parent_id = Column(String, ForeignKey("posts.post_id"), nullable=True)
    user = relationship("User", back_populates="posts")
    doctor = relationship("Doctor", back_populates="posts")
    replies = relationship("Post", back_populates="parent", foreign_keys=[parent_id])
    parent = relationship("Post", back_populates="replies", remote_side=[post_id])


Base.metadata.create_all(bind=engine)
