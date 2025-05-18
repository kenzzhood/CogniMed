from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from app.schema.post import Post


class UserModel(BaseModel):
    id: UUID = Field(..., example="4zb48f84-4865-3214-z7qw-6c654e48aga7")
    email: EmailStr
    username: str
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
    posts: list[Post] = []


class DoctorModel(BaseModel):
    id: UUID = Field(..., example="4zb48f84-4865-3214-z7qw-6c654e48aga7")
    email: EmailStr
    username: str
    name: str
    phone: str
    specialization: str
    hospital_name: str
    posts: list[Post] = []
