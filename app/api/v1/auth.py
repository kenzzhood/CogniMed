from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schema.auth import (
    AuthResponse,
    LoginRequest,
    RegisterUserRequest,
    RegisterDoctorRequest,
)
from app.utils.auth import create_access_token, authenticate_user
from app.db.base import get_db
from app.db.db_schema import User, Doctor
from app.db.user import add_user
from app.db.doctor import add_doctor
from app.utils.security import hash_password
from app.db.auth import add_user_auth
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login/{login_type}", status_code=status.HTTP_200_OK, response_model=AuthResponse
)
def login(request: LoginRequest, login_type: str, db: Session = Depends(get_db)):
    doctor = login_type == "doctor"

    user_or_doctor = authenticate_user(
        request.username, request.password, doctor=doctor, db=db
    )
    if not user_or_doctor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token(
        {"sub": request.username, "is_doctor": doctor, "id": user_or_doctor.id}
    )
    return AuthResponse(access_token=token)


@router.post(
    "/register/{register_type}",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse,
)
def register(
    request: RegisterUserRequest | RegisterDoctorRequest,
    register_type: str,
    db: Session = Depends(get_db),
):
    doctor = register_type == "doctor"
    existing_user = (
        db.query(Doctor if doctor else User)
        .filter(
            Doctor.email == request.email if doctor else User.email == request.email
        )
        .first()
        or db.query(Doctor if doctor else User)
        .filter(
            Doctor.username == request.username
            if doctor
            else User.username == request.username
        )
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{'Doctor' if doctor else 'User'} already registered",
        )

    hashed_password = hash_password(request.password)

    try:
        user_or_doctor = (
            add_doctor(
                name=request.name,
                email=request.email,
                username=request.username,
                phone=request.phone,
                specialization=request.specialization,
                hospital_name=request.hospital_name,
                db=db,
            )
            if doctor
            else add_user(
                email=request.email,
                username=request.username,
                name=request.name,
                phone=request.phone,
                date_of_birth=request.date_of_birth,
                gender=request.gender,
                blood_group=request.blood_group,
                relation_number=request.relation_number,
                family_doctor_name=request.family_doctor_name,
                family_doctor_number=request.family_doctor_number,
                height=request.height,
                weight=request.weight,
                aadhaar_number=request.aadhaar_number,
                db=db,
            )
        )
        add_user_auth(
            username=request.username,
            hashed_password=hashed_password,
            is_doctor=doctor,
            db=db,
        )
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integrity error: {str(e.orig)}",
        )
    token = create_access_token(
        {"sub": request.username, "is_doctor": doctor, "id": user_or_doctor.id}
    )
    return AuthResponse(access_token=token)
