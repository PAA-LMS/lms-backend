from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..models.users import User, CourseMaterial, AssignmentSubmission, StudentProfile, CourseWeek, Course, MaterialType, LecturerProfile
from ..schemas.users import AssignmentSubmission as AssignmentSubmissionSchema
from ..schemas.users import AssignmentSubmissionCreate, AssignmentSubmissionUpdate
from ..utils.auth import get_current_active_user, get_current_lecturer, get_current_student

router = APIRouter(prefix="/assignments", tags=["assignments"])

# Submit assignment (student)
@router.post("/submit", response_model=AssignmentSubmissionSchema, status_code=status.HTTP_201_CREATED)
def submit_assignment(
    submission: AssignmentSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)  # Only students can submit assignments
):
    """
    Submit an assignment (requires student privileges)
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
    
    # Check if assignment exists
    assignment = db.query(CourseMaterial).filter(CourseMaterial.id == submission.assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if assignment is of type "assignment"
    if assignment.material_type != MaterialType.ASSIGNMENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This material is not an assignment"
        )
    
    # Check if student already submitted this assignment
    existing_submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == submission.assignment_id,
        AssignmentSubmission.student_id == student_profile.id
    ).first()
    
    if existing_submission:
        # Update existing submission
        existing_submission.submission_url = submission.submission_url
        existing_submission.status = "submitted"  # Reset status to submitted
        db.commit()
        db.refresh(existing_submission)
        return existing_submission
    
    # Create new submission
    db_submission = AssignmentSubmission(
        assignment_id=submission.assignment_id,
        student_id=student_profile.id,
        submission_url=submission.submission_url,
        status="submitted"
    )
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

# Get all submissions for an assignment (lecturer)
@router.get("/material/{material_id}/submissions", response_model=List[AssignmentSubmissionSchema])
def get_assignment_submissions(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)  # Only lecturers can view all submissions
):
    """
    Get all submissions for a specific assignment (requires lecturer privileges)
    """
    # Get lecturer profile
    lecturer_profile = db.query(LecturerProfile).filter(
        LecturerProfile.user_id == current_user.id
    ).first()
    
    # Check if assignment exists
    assignment = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if assignment is of type "assignment"
    if assignment.material_type != MaterialType.ASSIGNMENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This material is not an assignment"
        )
    
    # Check if the lecturer owns this course
    week = db.query(CourseWeek).filter(CourseWeek.id == assignment.week_id).first()
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course week not found"
        )
    
    course = db.query(Course).filter(Course.id == week.course_id).first()
    if not course or course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view submissions for this assignment"
        )
    
    # Get all submissions
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == material_id
    ).all()
    
    return submissions

# Get student submission for an assignment
@router.get("/material/{material_id}/my-submission", response_model=AssignmentSubmissionSchema)
def get_student_submission(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a student's submission for a specific assignment (requires authentication)
    """
    # Check if user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their submissions"
        )
    
    # Get student profile
    student_profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()
    
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile not found"
        )
    
    # Check if assignment exists
    assignment = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if assignment is of type "assignment"
    if assignment.material_type != MaterialType.ASSIGNMENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This material is not an assignment"
        )
    
    # Get student's submission
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == material_id,
        AssignmentSubmission.student_id == student_profile.id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    return submission

# Update submission (lecturer - grade, feedback)
@router.put("/submissions/{submission_id}", response_model=AssignmentSubmissionSchema)
def update_submission(
    submission_id: int,
    submission_data: AssignmentSubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)  # Only lecturers can update submissions
):
    """
    Update an assignment submission (grade, feedback) - requires lecturer privileges
    """
    # Get lecturer profile
    lecturer_profile = db.query(LecturerProfile).filter(
        LecturerProfile.user_id == current_user.id
    ).first()
    
    # Find the submission
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # Get the assignment
    assignment = db.query(CourseMaterial).filter(
        CourseMaterial.id == submission.assignment_id
    ).first()
    
    # Check if lecturer owns this course
    week = db.query(CourseWeek).filter(CourseWeek.id == assignment.week_id).first()
    course = db.query(Course).filter(Course.id == week.course_id).first()
    
    if not course or course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update submissions for this assignment"
        )
    
    # Update submission
    submission_data_dict = submission_data.dict(exclude_unset=True)
    for key, value in submission_data_dict.items():
        setattr(submission, key, value)
    
    # If grade or feedback is provided, set status to "graded"
    if submission_data.grade or submission_data.feedback:
        submission.status = "graded"
    
    db.commit()
    db.refresh(submission)
    return submission 