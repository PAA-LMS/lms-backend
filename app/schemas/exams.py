from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional

class ExamBase(BaseModel):
    title: str
    description: str
    course_id: int
    start_time: datetime
    end_time: datetime
    total_marks: float

class ExamCreate(ExamBase):
    pass

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_marks: Optional[float] = None

class Exam(ExamBase):
    id: int
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class ExamSubmissionBase(BaseModel):
    answers: Dict[str, str]  # Question ID to answer mapping

class ExamSubmissionCreate(ExamSubmissionBase):
    pass

class ExamSubmission(ExamSubmissionBase):
    id: int
    exam_id: int
    student_id: int
    submission_time: datetime
    marks: Optional[float] = None
    feedback: Optional[str] = None

    class Config:
        orm_mode = True 