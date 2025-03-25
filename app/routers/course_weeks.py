from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..models.users import User, Course, CourseWeek, LecturerProfile
from ..schemas.users import CourseWeek as CourseWeekSchema, CourseWeekCreate, CourseWeekUpdate
from ..utils.auth import get_current_active_user, get_current_lecturer

router = APIRouter(prefix="/course-weeks", tags=["course weeks"])

# Create a new course week
@router.post("/", response_model=CourseWeekSchema, status_code=status.HTTP_201_CREATED)
def create_course_week(
    week: CourseWeekCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)  # Only lecturers can create weeks
):
    """
    Create a new course week (requires lecturer privileges)
    """
    # Check if course exists
    course = db.query(Course).filter(Course.id == week.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get lecturer profile
    lecturer_profile = db.query(LecturerProfile).filter(
        LecturerProfile.user_id == current_user.id
    ).first()
    
    # Check if lecturer owns this course
    if course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add weeks to this course"
        )
    
    # Create course week
    db_week = CourseWeek(
        course_id=week.course_id,
        title=week.title,
        description=week.description,
        week_number=week.week_number
    )
    
    db.add(db_week)
    db.commit()
    db.refresh(db_week)
    return db_week

# Get weeks for a course by course_id param
@router.get("/course/{course_id}", response_model=List[CourseWeekSchema])
def read_course_weeks_by_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all weeks for a specific course (requires authentication)
    """
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    weeks = db.query(CourseWeek).filter(CourseWeek.course_id == course_id).order_by(CourseWeek.week_number).all()
    return weeks

# Get a specific week
@router.get("/{course_id}/{week_id}", response_model=CourseWeekSchema)
def read_course_week(
    course_id: int,
    week_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific course week by ID (requires authentication)
    """
    week = db.query(CourseWeek).filter(
        CourseWeek.id == week_id,
        CourseWeek.course_id == course_id
    ).first()
    
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course week not found"
        )
    
    return week

# Update a course week by ID
@router.put("/{week_id}", response_model=CourseWeekSchema)
def update_course_week_by_id(
    week_id: int,
    week_data: CourseWeekUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)  # Only lecturers can update weeks
):
    """
    Update a course week (requires lecturer privileges)
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
    
    # Find the week
    week = db.query(CourseWeek).filter(CourseWeek.id == week_id).first()
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course week not found"
        )
    
    # Check if course exists and belongs to lecturer
    course = db.query(Course).filter(Course.id == week.course_id).first()
    if not course or course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this week"
        )
    
    # Update week fields
    week_data_dict = week_data.dict(exclude_unset=True)
    for key, value in week_data_dict.items():
        setattr(week, key, value)
    
    db.commit()
    db.refresh(week)
    return week

# Delete a course week
@router.delete("/{week_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course_week_by_id(
    week_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)  # Only lecturers can delete weeks
):
    """
    Delete a course week (requires lecturer privileges)
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
    
    # Find the week
    week = db.query(CourseWeek).filter(CourseWeek.id == week_id).first()
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course week not found"
        )
    
    # Check if course exists and belongs to lecturer
    course = db.query(Course).filter(Course.id == week.course_id).first()
    if not course or course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this week"
        )
    
    db.delete(week)
    db.commit()
    return None 