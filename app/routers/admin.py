from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database.database import get_db
from ..models.users import User, UserRole, LecturerProfile, StudentProfile
from ..schemas.users import User as UserSchema, UserCreate, UserUpdate
from ..utils.auth import get_current_admin, get_password_hash

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[UserSchema])
async def get_all_users(
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get all users (requires admin privileges)
    Optional query parameter 'role' to filter by role (lecturer, student, admin)
    """
    query = db.query(User)
    
    if role:
        if role not in [UserRole.LECTURER, UserRole.STUDENT, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {UserRole.LECTURER}, {UserRole.STUDENT}, {UserRole.ADMIN}"
            )
        query = query.filter(User.role == role)
    
    users = query.all()
    return users

@router.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Create a new user (requires admin privileges)
    """
    # Check if email or username already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role=user_data.role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create profile based on role
    if user_data.role == UserRole.LECTURER and user_data.lecturer_profile:
        lecturer_profile = LecturerProfile(
            user_id=db_user.id,
            department=user_data.lecturer_profile.department,
            bio=user_data.lecturer_profile.bio,
            qualification=user_data.lecturer_profile.qualification
        )
        db.add(lecturer_profile)
        db.commit()
    
    elif user_data.role == UserRole.STUDENT and user_data.student_profile:
        student_profile = StudentProfile(
            user_id=db_user.id,
            enrollment_number=user_data.student_profile.enrollment_number,
            semester=user_data.student_profile.semester,
            program=user_data.student_profile.program
        )
        db.add(student_profile)
        db.commit()
    
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get a specific user by ID (requires admin privileges)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Update a user (requires admin privileges)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    user_data_dict = user_data.dict(exclude_unset=True)
    
    # Handle email uniqueness check
    if user_data.email and user_data.email != user.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Handle username uniqueness check
    if user_data.username and user_data.username != user.username:
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    for key, value in user_data_dict.items():
        # Skip nested objects (profiles)
        if key not in ["lecturer_profile", "student_profile"]:
            setattr(user, key, value)
    
    # Update lecturer profile if present
    if user.role == UserRole.LECTURER and user_data.lecturer_profile:
        lecturer_profile = db.query(LecturerProfile).filter(LecturerProfile.user_id == user.id).first()
        if lecturer_profile:
            for key, value in user_data.lecturer_profile.dict(exclude_unset=True).items():
                setattr(lecturer_profile, key, value)
    
    # Update student profile if present
    if user.role == UserRole.STUDENT and user_data.student_profile:
        student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        if student_profile:
            for key, value in user_data.student_profile.dict(exclude_unset=True).items():
                setattr(student_profile, key, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Delete a user (requires admin privileges)
    """
    # Don't allow admin to delete themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete lecturer profile if exists
    if user.role == UserRole.LECTURER:
        lecturer_profile = db.query(LecturerProfile).filter(LecturerProfile.user_id == user.id).first()
        if lecturer_profile:
            db.delete(lecturer_profile)
    
    # Delete student profile if exists
    if user.role == UserRole.STUDENT:
        student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        if student_profile:
            db.delete(student_profile)
    
    db.delete(user)
    db.commit()
    return None 