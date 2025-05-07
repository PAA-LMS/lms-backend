from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database.database import get_db
from ..models.users import User, Course, LecturerProfile, StudentProfile
from ..models.exams import Exam, ExamSubmission as ExamSubmissionModel
from ..schemas.exams import Exam as ExamSchema, ExamCreate, ExamUpdate, ExamSubmission, ExamSubmissionBase
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
    
    # Create exam
    db_exam = Exam(
        course_name=exam.course_name,
        title=exam.title,
        description=exam.description,
        exam_url=exam.exam_url,
        due_date=exam.due_date,
        status="active",
        created_by=current_user.id
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
    
    # Get exams by course name
    exams = db.query(Exam).filter(Exam.course_name == course.title).all()
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
    submission: ExamSubmissionBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """
    Submit exam (requires student privileges)
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
    
    # Check if student has already submitted this exam
    existing_submission = db.query(ExamSubmissionModel).filter(
        ExamSubmissionModel.exam_id == exam_id,
        ExamSubmissionModel.student_id == student_profile.id
    ).first()
    
    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted this exam"
        )
    
    current_time = datetime.utcnow()
    if current_time > exam.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam submission deadline has passed"
        )
    
    # Create submission
    db_submission = ExamSubmissionModel(
        exam_id=exam_id,
        student_id=student_profile.id,
        submission_url=submission.submission_url,
        status="submitted",
        submitted_at=current_time
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
    
    # Find lecturer's courses
    lecturer_courses = db.query(Course).filter(Course.lecturer_id == lecturer_profile.id).all()
    course_titles = [course.title for course in lecturer_courses]
    
    # Check if exam course belongs to lecturer
    if exam.course_name not in course_titles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload file for this exam"
        )
    
    # Save file
    file_location = f"exam_files/{exam_id}_{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    # Update exam with file URL
    exam.exam_url = file_location
    db.commit()
    
    return {"message": "File uploaded successfully"}

# Check if student has already submitted an exam
@router.get("/{exam_id}/submission-status", response_model=dict)
def check_submission_status(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """
    Check if the student has already submitted this exam
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
    
    # Verify exam exists
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Check if student has already submitted this exam
    existing_submission = db.query(ExamSubmissionModel).filter(
        ExamSubmissionModel.exam_id == exam_id,
        ExamSubmissionModel.student_id == student_profile.id
    ).first()
    
    return {"submitted": existing_submission is not None}

# Get exam submissions (lecturer only)
@router.get("/{exam_id}/submissions", response_model=List[dict])
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
    
    # Find lecturer's courses
    lecturer_courses = db.query(Course).filter(Course.lecturer_id == lecturer_profile.id).all()
    course_titles = [course.title for course in lecturer_courses]
    
    # Check if exam course belongs to lecturer
    if exam.course_name not in course_titles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view submissions for this exam"
        )
    
    # First try a simple query to get the count
    count = db.query(ExamSubmissionModel).filter(ExamSubmissionModel.exam_id == exam_id).count()
    print(f"DEBUG: Found {count} submissions for exam {exam_id}")

    if count == 0:
        return []

    # Get submissions with student information
    try:
        query = db.query(
            ExamSubmissionModel, 
            StudentProfile.enrollment_number.label("student_number"), 
            User.first_name,
            User.last_name,
            User.email
        ).join(
            StudentProfile, ExamSubmissionModel.student_id == StudentProfile.id
        ).join(
            User, StudentProfile.user_id == User.id
        ).filter(
            ExamSubmissionModel.exam_id == exam_id
        )
        
        print(f"DEBUG: Query SQL: {str(query)}")
        submissions = query.all()
        print(f"DEBUG: Found {len(submissions)} submissions with join")
        
        # Format the response
        result = []
        for submission, student_number, first_name, last_name, email in submissions:
            result.append({
                "id": submission.id,
                "exam_id": submission.exam_id,
                "student_id": submission.student_id,
                "student_number": student_number,
                "student_name": f"{first_name} {last_name}",
                "student_email": email,
                "submission_url": submission.submission_url,
                "status": submission.status,
                "grade": submission.grade,
                "feedback": submission.feedback,
                "submitted_at": submission.submitted_at,
                "graded_at": submission.graded_at
            })
        
        print(f"DEBUG: Returning {len(result)} formatted submissions")
        return result
    except Exception as e:
        print(f"ERROR in get_exam_submissions: {str(e)}")
        # In case of error, return a simple list of submissions
        submissions = db.query(ExamSubmissionModel).filter(
            ExamSubmissionModel.exam_id == exam_id
        ).all()
        
        return [
            {
                "id": submission.id,
                "exam_id": submission.exam_id,
                "student_id": submission.student_id,
                "student_number": "N/A",
                "student_name": "Unknown Student",
                "student_email": "N/A",
                "submission_url": submission.submission_url,
                "status": submission.status,
                "grade": submission.grade,
                "feedback": submission.feedback,
                "submitted_at": submission.submitted_at,
                "graded_at": submission.graded_at
            }
            for submission in submissions
        ]

# Update an exam (lecturer only)
@router.put("/{exam_id}", response_model=ExamSchema)
def update_exam(
    exam_id: int,
    exam_update: ExamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)
):
    """
    Update an exam (requires lecturer privileges)
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
    
    # Verify exam exists
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Find lecturer's courses
    lecturer_courses = db.query(Course).filter(Course.lecturer_id == lecturer_profile.id).all()
    course_titles = [course.title for course in lecturer_courses]
    
    # Check if exam course belongs to lecturer
    if exam.course_name not in course_titles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this exam"
        )
    
    # Update exam fields
    if exam_update.title is not None:
        exam.title = exam_update.title
    if exam_update.description is not None:
        exam.description = exam_update.description
    if exam_update.course_name is not None:
        exam.course_name = exam_update.course_name
    if exam_update.exam_url is not None:
        exam.exam_url = exam_update.exam_url
    if exam_update.due_date is not None:
        exam.due_date = exam_update.due_date
    if exam_update.status is not None:
        exam.status = exam_update.status
    
    db.commit()
    db.refresh(exam)
    return exam

# Delete an exam (lecturer only)
@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)
):
    """
    Delete an exam (requires lecturer privileges)
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
    
    # Verify exam exists
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Find lecturer's courses
    lecturer_courses = db.query(Course).filter(Course.lecturer_id == lecturer_profile.id).all()
    course_titles = [course.title for course in lecturer_courses]
    
    # Check if exam course belongs to lecturer
    if exam.course_name not in course_titles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this exam"
        )
    
    try:
        # First delete all submissions associated with this exam
        db.query(ExamSubmissionModel).filter(
            ExamSubmissionModel.exam_id == exam_id
        ).delete(synchronize_session=False)
        
        # Then delete the exam
        db.delete(exam)
        db.commit()
        
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete exam: {str(e)}"
        )

# Debug endpoint to check all exam submissions (for development only)
@router.get("/debug/all-submissions", response_model=List[dict])
def debug_all_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)
):
    """
    Debug endpoint to get all submissions in the system
    """
    try:
        # First try with a simpler query to just count
        count = db.query(ExamSubmissionModel).count()
        print(f"DEBUG: Total submissions in system: {count}")
        
        if count == 0:
            return []
        
        # Now try the complex query
        submissions = db.query(
            ExamSubmissionModel,
            StudentProfile.enrollment_number.label("student_number"),
            Exam.title.label("exam_title"),
            User.first_name,
            User.last_name
        ).join(
            StudentProfile, ExamSubmissionModel.student_id == StudentProfile.id
        ).join(
            User, StudentProfile.user_id == User.id
        ).join(
            Exam, ExamSubmissionModel.exam_id == Exam.id
        ).all()
        
        result = []
        for submission, student_number, exam_title, first_name, last_name in submissions:
            result.append({
                "id": submission.id,
                "exam_id": submission.exam_id,
                "exam_title": exam_title,
                "student_id": submission.student_id,
                "student_number": student_number,
                "student_name": f"{first_name} {last_name}",
                "submission_url": submission.submission_url,
                "submitted_at": submission.submitted_at
            })
        
        return result
    except Exception as e:
        print(f"ERROR in debug_all_submissions: {str(e)}")
        # In case of error, return basic submission info
        submissions = db.query(ExamSubmissionModel).all()
        return [
            {
                "id": submission.id,
                "exam_id": submission.exam_id,
                "exam_title": "Unknown",
                "student_id": submission.student_id,
                "student_number": "N/A",
                "student_name": "Unknown",
                "submission_url": submission.submission_url,
                "submitted_at": submission.submitted_at
            }
            for submission in submissions
        ] 