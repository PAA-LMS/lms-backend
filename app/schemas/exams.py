from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional

class ExamBase(BaseModel):
    title: str
    description: str
    course_name: str
    exam_url: str
    due_date: datetime

class ExamCreate(ExamBase):
    pass

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    course_name: Optional[str] = None
    exam_url: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None

class Exam(ExamBase):
    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class ExamSubmissionBase(BaseModel):
    submission_url: str  # Google Drive URL for the submission

class ExamSubmissionCreate(ExamSubmissionBase):
    pass

class ExamSubmission(ExamSubmissionBase):
    id: int
    exam_id: int
    student_id: int
    status: str
    grade: Optional[str] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True 