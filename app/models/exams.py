from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.database import Base

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    exam_url = Column(String)
    due_date = Column(DateTime, nullable=False)
    status = Column(String, default="active")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    submissions = relationship("ExamSubmission", back_populates="exam")

class ExamSubmission(Base):
    __tablename__ = "exam_submissions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    submission_url = Column(String, nullable=False)  # Google Drive URL for the submission
    status = Column(String, default="submitted")
    grade = Column(String, nullable=True)
    feedback = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exam = relationship("Exam", back_populates="submissions")
    student = relationship("StudentProfile", back_populates="exam_submissions") 