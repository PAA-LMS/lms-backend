from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..models.users import User, Course, LecturerProfile
from ..schemas.users import Course as CourseSchema, CourseCreate, CourseUpdate
from ..utils.auth import get_current_active_user, get_current_lecturer

router = APIRouter(prefix="/courses", tags=["courses"])

# Create a new course (lecturer only)
@router.post("/", response_model=CourseSchema, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)
):
    """
    Create a new course (requires lecturer privileges)
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
    
    # Create course
    db_course = Course(
        title=course.title,
        description=course.description,
        lecturer_id=lecturer_profile.id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

# Get all courses
@router.get("/", response_model=List[CourseSchema])
def read_courses(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all courses (requires authentication)
    """
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

# Get courses by lecturer
@router.get("/my-courses", response_model=List[CourseSchema])
def read_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)
):
    """
    Get all courses created by the current lecturer (requires lecturer privileges)
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
    
    courses = db.query(Course).filter(Course.lecturer_id == lecturer_profile.id).all()
    return courses

# Get a specific course
@router.get("/{course_id}", response_model=CourseSchema)
def read_course(
    course_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific course by ID (requires authentication)
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# Update a course (lecturer only)
@router.put("/{course_id}", response_model=CourseSchema)
def update_course(
    course_id: int,
    course: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)
):
    """
    Update a course (requires lecturer privileges and only own courses)
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
    
    # Find course
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Ensure lecturer owns this course
    if db_course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course"
        )
    
    # Update course fields
    course_data = course.dict(exclude_unset=True)
    for key, value in course_data.items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course

# Delete a course (lecturer only)
@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)
):
    """
    Delete a course (requires lecturer privileges and only own courses)
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
    
    # Find course
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Ensure lecturer owns this course
    if db_course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this course"
        )
    
    db.delete(db_course)
    db.commit()
    return None 