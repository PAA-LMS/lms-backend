from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..models.users import User, Course, CourseWeek, CourseMaterial, LecturerProfile
from ..schemas.users import CourseMaterial as CourseMaterialSchema, CourseMaterialCreate, CourseMaterialUpdate
from ..utils.auth import get_current_active_user, get_current_lecturer

router = APIRouter(prefix="/course-materials", tags=["course materials"])

# Create a new course material
@router.post("/", response_model=CourseMaterialSchema, status_code=status.HTTP_201_CREATED)
def create_course_material(
    material: CourseMaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)  # Only lecturers can create materials
):
    """
    Create a new course material (requires lecturer privileges)
    """
    # Get lecturer profile
    lecturer_profile = db.query(LecturerProfile).filter(
        LecturerProfile.user_id == current_user.id
    ).first()
    
    # Check if week exists
    week = db.query(CourseWeek).filter(CourseWeek.id == material.week_id).first()
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course week not found"
        )
    
    # Check if course exists and belongs to lecturer
    course = db.query(Course).filter(Course.id == week.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course.lecturer_id != lecturer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add materials to this course"
        )
    
    # Create course material
    db_material = CourseMaterial(
        week_id=material.week_id,
        title=material.title,
        description=material.description,
        material_type=material.material_type,
        content=material.content
    )
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

# Get materials for a specific week by week_id
@router.get("/week/{week_id}", response_model=List[CourseMaterialSchema])
def read_materials_by_week(
    week_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all materials for a specific course week (requires authentication)
    """
    # Check if week exists
    week = db.query(CourseWeek).filter(CourseWeek.id == week_id).first()
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course week not found"
        )
    
    materials = db.query(CourseMaterial).filter(CourseMaterial.week_id == week_id).all()
    return materials

# Get a specific material by ID
@router.get("/{material_id}", response_model=CourseMaterialSchema)
def read_material_by_id(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific course material by ID (requires authentication)
    """
    material = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    return material

# Update a course material
@router.put("/{material_id}", response_model=CourseMaterialSchema)
def update_material(
    material_id: int,
    material_data: CourseMaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)  # Only lecturers can update materials
):
    """
    Update a course material (requires lecturer privileges)
    """
    # Get lecturer profile
    lecturer_profile = db.query(LecturerProfile).filter(
        LecturerProfile.user_id == current_user.id
    ).first()
    
    # Find the material
    material = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Check if week exists
    week = db.query(CourseWeek).filter(CourseWeek.id == material.week_id).first()
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
            detail="Not authorized to update materials for this course"
        )
    
    # Update material fields
    material_data_dict = material_data.dict(exclude_unset=True)
    for key, value in material_data_dict.items():
        setattr(material, key, value)
    
    db.commit()
    db.refresh(material)
    return material

# Delete a course material
@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)  # Only lecturers can delete materials
):
    """
    Delete a course material (requires lecturer privileges)
    """
    # Get lecturer profile
    lecturer_profile = db.query(LecturerProfile).filter(
        LecturerProfile.user_id == current_user.id
    ).first()
    
    # Find the material
    material = db.query(CourseMaterial).filter(CourseMaterial.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Check if week exists
    week = db.query(CourseWeek).filter(CourseWeek.id == material.week_id).first()
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
            detail="Not authorized to delete materials for this course"
        )
    
    db.delete(material)
    db.commit()
    return None 