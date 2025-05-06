from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.database import Base

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    total_marks = Column(Float, nullable=False)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="exams")
    submissions = relationship("ExamSubmission", back_populates="exam")

class ExamSubmission(Base):
    __tablename__ = "exam_submissions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    answers = Column(JSON, nullable=False)  # Stores question-answer pairs
    submission_time = Column(DateTime, default=datetime.utcnow)
    marks = Column(Float, nullable=True)
    feedback = Column(String, nullable=True)

    # Relationships
    exam = relationship("Exam", back_populates="submissions")
    student = relationship("StudentProfile", back_populates="exam_submissions") 