from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.database import Base

# Define user roles
class UserRole:
    LECTURER = "lecturer"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # "lecturer" or "student"
    first_name = Column(String)
    last_name = Column(String)
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
    department = Column(String)
    bio = Column(String)
    qualification = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="lecturer_profile")
    courses = relationship("Course", back_populates="lecturer")

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    enrollment_number = Column(String, unique=True, index=True)
    semester = Column(Integer)
    program = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="student_profile")
    
# Course model to be used with lecturer
class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    lecturer_id = Column(Integer, ForeignKey("lecturer_profiles.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    lecturer = relationship("LecturerProfile", back_populates="courses") 