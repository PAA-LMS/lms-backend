from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Base Schema for Lecturer Profile
class LecturerProfileBase(BaseModel):
    department: Optional[str] = None
    bio: Optional[str] = None
    qualification: Optional[str] = None

class LecturerProfileCreate(LecturerProfileBase):
    pass

class LecturerProfileUpdate(LecturerProfileBase):
    pass

class LecturerProfile(LecturerProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Base Schema for Student Profile
class StudentProfileBase(BaseModel):
    enrollment_number: Optional[str] = None
    semester: Optional[int] = None
    program: Optional[str] = None

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileUpdate(StudentProfileBase):
    pass

class StudentProfile(StudentProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str

class UserCreate(UserBase):
    password: str
    lecturer_profile: Optional[LecturerProfileCreate] = None
    student_profile: Optional[StudentProfileCreate] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    lecturer_profile: Optional[LecturerProfileUpdate] = None
    student_profile: Optional[StudentProfileUpdate] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    lecturer_profile: Optional[LecturerProfile] = None
    student_profile: Optional[StudentProfile] = None

    class Config:
        from_attributes = True

# Token schemas for authentication
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Course Schemas
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class Course(CourseBase):
    id: int
    lecturer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 