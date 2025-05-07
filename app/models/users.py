from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.database import Base

# Define user roles
class UserRole:
    LECTURER = "lecturer"
    STUDENT = "student"
    ADMIN = "admin"

# Define material types
class MaterialType:
    LINK = "link"
    DRIVE_URL = "drive_url"
    ASSIGNMENT = "assignment"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(50))  # "lecturer" or "student"
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship with profile based on role
    lecturer_profile = relationship("LecturerProfile", back_populates="user", uselist=False)
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)

class LecturerProfile(Base):
    __tablename__ = "lecturer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    department = Column(String(100))
    bio = Column(String(500))
    qualification = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="lecturer_profile")
    courses = relationship("Course", back_populates="lecturer")

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    enrollment_number = Column(String(50), unique=True, index=True)
    semester = Column(Integer)
    program = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="student_profile")
    # Add relationship to assignment submissions
    submissions = relationship("AssignmentSubmission", back_populates="student")
    exam_submissions = relationship("ExamSubmission", back_populates="student")
    payment_submissions = relationship("PaymentSubmission", back_populates="student")

# Course model to be used with lecturer
class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    description = Column(String(500))
    lecturer_id = Column(Integer, ForeignKey("lecturer_profiles.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    lecturer = relationship("LecturerProfile", back_populates="courses")
    weeks = relationship("CourseWeek", back_populates="course", cascade="all, delete-orphan")

# CourseWeek model to organize materials by week
class CourseWeek(Base):
    __tablename__ = "course_weeks"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String(200))
    description = Column(String(500))
    week_number = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="weeks")
    materials = relationship("CourseMaterial", back_populates="week", cascade="all, delete-orphan")

# CourseMaterial model for individual materials (links, docs, etc.)
class CourseMaterial(Base):
    __tablename__ = "course_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("course_weeks.id"))
    title = Column(String(200))
    description = Column(String(500))
    material_type = Column(String(50))  # e.g., "drive_url", "file", "link", "assignment"
    content = Column(Text)  # Text type doesn't need length specification
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    week = relationship("CourseWeek", back_populates="materials")
    # Add relationship to submissions if this is an assignment
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")

# New AssignmentSubmission model for student submissions
class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("course_materials.id"))
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    submission_url = Column(Text)  # Google Drive URL for the submitted document
    submitted_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    status = Column(String(50), default="submitted")  # e.g., "submitted", "graded"
    grade = Column(String(50), nullable=True)  # Optional grade
    feedback = Column(Text, nullable=True)  # Optional feedback
    
    # Relationships
    assignment = relationship("CourseMaterial", back_populates="submissions")
    student = relationship("StudentProfile", back_populates="submissions") 