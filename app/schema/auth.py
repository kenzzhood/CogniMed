from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    name: str
    phone: str
    date_of_birth: str
    gender: str
    blood_group: str
    relation_number: str
    family_doctor_name: str
    family_doctor_number: str
    height: str
    weight: str
    aadhaar_number: str


class RegisterDoctorRequest(BaseModel):
    username: str
    name: str
    email: EmailStr
    phone: str
    password: str
    specialization: str
    hospital_name: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    is_doctor: Optional[bool] = None
    id: Optional[UUID] = None
