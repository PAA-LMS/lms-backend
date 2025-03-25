from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..models.users import User, UserRole, LecturerProfile, StudentProfile
from ..schemas.users import UserCreate, User as UserSchema, UserUpdate
from ..utils.auth import get_password_hash, get_current_active_user, get_current_lecturer

router = APIRouter(prefix="/users", tags=["users"])

# Create a new user
@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user (lecturer or student)
    """
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create lecturer profile if it's a lecturer
    if user.role == UserRole.LECTURER and user.lecturer_profile:
        lecturer_profile = LecturerProfile(
            user_id=db_user.id,
            department=user.lecturer_profile.department,
            bio=user.lecturer_profile.bio,
            qualification=user.lecturer_profile.qualification
        )
        db.add(lecturer_profile)
        db.commit()
        db.refresh(lecturer_profile)
    
    # Create student profile if it's a student
    if user.role == UserRole.STUDENT and user.student_profile:
        student_profile = StudentProfile(
            user_id=db_user.id,
            enrollment_number=user.student_profile.enrollment_number,
            semester=user.student_profile.semester,
            program=user.student_profile.program
        )
        db.add(student_profile)
        db.commit()
        db.refresh(student_profile)
    
    # Refresh user to get the profiles
    db.refresh(db_user)
    return db_user

# Get all users
@router.get("/", response_model=List[UserSchema])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all users (requires authentication)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Get user by ID
@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific user by ID (requires authentication)
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Update user
@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a user (requires authentication and only own profile unless lecturer)
    """
    # Only allow users to update themselves unless they are lecturers
    if current_user.id != user_id and current_user.role != UserRole.LECTURER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields if provided
    user_data = user.dict(exclude_unset=True)
    
    # Handle nested lecturer profile update
    if "lecturer_profile" in user_data and db_user.role == UserRole.LECTURER:
        lecturer_data = user_data.pop("lecturer_profile")
        if db_user.lecturer_profile and lecturer_data:
            for key, value in lecturer_data.items():
                setattr(db_user.lecturer_profile, key, value)
    
    # Handle nested student profile update
    if "student_profile" in user_data and db_user.role == UserRole.STUDENT:
        student_data = user_data.pop("student_profile")
        if db_user.student_profile and student_data:
            for key, value in student_data.items():
                setattr(db_user.student_profile, key, value)
    
    # Update remaining user fields
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# Delete user
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_lecturer)  # Only lecturers can delete users
):
    """
    Delete a user (requires lecturer privileges)
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return None 