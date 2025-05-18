from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
import cloudinary.uploader
from app.db.priscription import add_priscription, delete_priscription
from app.utils.med_record_processor import extract_med_info_save

router = APIRouter(prefix="/priscription", tags=["priscription"])


@router.post("/upload")
def upload_priscription(
    doctor_name: str = Form(...),
    visit_date: str = Form(...),
    visit_time: str = Form(...),
    hospital_name: str = Form(...),
    username: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # TODO: check whether the username exists or not
    try:
        upload_result = cloudinary.uploader.upload(file.file, access_mode="public")
        file_url = upload_result.get("secure_url")
        if not file_url:
            raise HTTPException(
                status_code=500, detail="Failed to upload image to Cloudinary"
            )
        priscription = add_priscription(
            db=db,
            doctor_name=doctor_name,
            visit_date=visit_date,
            visit_time=visit_time,
            hospital_name=hospital_name,
            username=username,
            file_url=file_url,
        )
        print("Extracting medical information from the image...")
        file.file.seek(0)
        extract_med_info_save(
            image_bytes=file.file.read(),
            username=username,
        )
        return {
            "detail": "Priscription uploaded successfully",
            "file_url": file_url,
            "id": priscription.id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{priscription_id}")
def delete_priscription_api(priscription_id: int, db: Session = Depends(get_db)):
    success = delete_priscription(db, priscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Priscription not found")
    return {"detail": "Priscription deleted successfully"}


@router.get("/user/{username}")
def get_user_priscriptions(username: str, db: Session = Depends(get_db)):
    """
    Get all prescriptions for a given username.
    """
    from app.db.db_schema import Priscription

    priscriptions = (
        db.query(Priscription).filter(Priscription.username == username).all()
    )
    return priscriptions
