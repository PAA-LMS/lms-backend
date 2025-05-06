from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database.database import get_db
from ..models.users import User, Course, LecturerProfile, StudentProfile
from ..schemas.exams import Exam as ExamSchema, ExamCreate, ExamUpdate, ExamSubmission
from ..utils.auth import get_current_active_user, get_current_lecturer, get_current_student

router = APIRouter(prefix="/exams", tags=["exams"])

# Create a new exam (lecturer only)
@router.post("/", response_model=ExamSchema, status_code=status.HTTP_201_CREATED)
def create_exam(
    exam: ExamCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)
):
    """
    Create a new exam (requires lecturer privileges)
    """
    # Get lecturer profile
    lecturer_profile = db.query(LecturerProfile).filter(
        LecturerProfile.user_id == current_user.id
    ).first()
    
    if not lecturer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lecturer profile not found"
        )
    
    # Verify course exists and belongs to lecturer
    course = db.query(Course).filter(Course.id == exam.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create exam for this course"
        )
    
    # Create exam
    db_exam = Exam(
        title=exam.title,
        description=exam.description,
        course_id=exam.course_id,
        start_time=exam.start_time,
        end_time=exam.end_time,
        total_marks=exam.total_marks
    )
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

# Get all exams for a course
@router.get("/course/{course_id}", response_model=List[ExamSchema])
def read_course_exams(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all exams for a specific course (requires authentication)
    """
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    exams = db.query(Exam).filter(Exam.course_id == course_id).all()
    return exams

# Get a specific exam
@router.get("/{exam_id}", response_model=ExamSchema)
def read_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific exam by ID (requires authentication)
    """
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam

# Submit exam answers (student only)
@router.post("/{exam_id}/submit", response_model=ExamSubmission)
def submit_exam(
    exam_id: int,
    submission: ExamSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """
    Submit exam answers (requires student privileges)
    """
    # Get student profile
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile not found"
        )
    
    # Verify exam exists and is active
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    current_time = datetime.utcnow()
    if current_time < exam.start_time or current_time > exam.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam is not currently active"
        )
    
    # Create submission
    db_submission = ExamSubmission(
        exam_id=exam_id,
        student_id=student_profile.id,
        answers=submission.answers,
        submission_time=current_time
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

# Upload exam file (lecturer only)
@router.post("/{exam_id}/upload", status_code=status.HTTP_201_CREATED)
def upload_exam_file(
    exam_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)
):
    """
    Upload exam file (requires lecturer privileges)
    """
    # Get lecturer profile
    lecturer_profile = db.query(LecturerProfile).filter(
        LecturerProfile.user_id == current_user.id
    ).first()
    
    if not lecturer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lecturer profile not found"
        )
    
    # Verify exam exists and belongs to lecturer
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    course = db.query(Course).filter(Course.id == exam.course_id).first()
    if course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload file for this exam"
        )
    
    # Save file
    file_location = f"exam_files/{exam_id}_{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    # Update exam with file path
    exam.file_path = file_location
    db.commit()
    
    return {"message": "File uploaded successfully"}

# Get exam submissions (lecturer only)
@router.get("/{exam_id}/submissions", response_model=List[ExamSubmission])
def get_exam_submissions(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)
):
    """
    Get all submissions for an exam (requires lecturer privileges)
    """
    # Get lecturer profile
    lecturer_profile = db.query(LecturerProfile).filter(
        LecturerProfile.user_id == current_user.id
    ).first()
    
    if not lecturer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lecturer profile not found"
        )
    
    # Verify exam exists and belongs to lecturer
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    course = db.query(Course).filter(Course.id == exam.course_id).first()
    if course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view submissions for this exam"
        )
    
    submissions = db.query(ExamSubmission).filter(ExamSubmission.exam_id == exam_id).all()
    return submissions 