from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Union
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

# Assignment Submission Schemas
class AssignmentSubmissionBase(BaseModel):
    submission_url: str
    
class AssignmentSubmissionCreate(AssignmentSubmissionBase):
    assignment_id: int

class AssignmentSubmissionUpdate(BaseModel):
    submission_url: Optional[str] = None
    status: Optional[str] = None
    grade: Optional[str] = None
    feedback: Optional[str] = None

class AssignmentSubmission(AssignmentSubmissionBase):
    id: int
    assignment_id: int
    student_id: int
    submitted_at: datetime
    updated_at: datetime
    status: str
    grade: Optional[str] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True

# Course Material Schemas
class CourseMaterialBase(BaseModel):
    title: str
    description: Optional[str] = None
    material_type: str  # e.g., "drive_url", "file", "link", "assignment"
    content: str  # URL, embedded content, etc.

class CourseMaterialCreate(CourseMaterialBase):
    week_id: int

class CourseMaterialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    material_type: Optional[str] = None
    content: Optional[str] = None

class CourseMaterial(CourseMaterialBase):
    id: int
    week_id: int
    created_at: datetime
    updated_at: datetime
    submissions: List[AssignmentSubmission] = []

    class Config:
        from_attributes = True

# Course Week Schemas
class CourseWeekBase(BaseModel):
    title: str
    description: Optional[str] = None
    week_number: int

class CourseWeekCreate(CourseWeekBase):
    course_id: int

class CourseWeekUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    week_number: Optional[int] = None

class CourseWeek(CourseWeekBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    materials: List[CourseMaterial] = []

    class Config:
        from_attributes = True

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
    weeks: List[CourseWeek] = []

    class Config:
        from_attributes = True 