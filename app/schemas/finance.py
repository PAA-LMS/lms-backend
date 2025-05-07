from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Payment Announcement Schemas
class PaymentAnnouncementBase(BaseModel):
    title: str
    description: str
    amount: str
    payment_details: str
    due_date: datetime

class PaymentAnnouncementCreate(PaymentAnnouncementBase):
    pass

class PaymentAnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[str] = None
    payment_details: Optional[str] = None
    due_date: Optional[datetime] = None

class PaymentAnnouncementResponse(PaymentAnnouncementBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Payment Submission Schemas
class PaymentSubmissionBase(BaseModel):
    announcement_id: int
    payment_slip_url: str
    amount_paid: str
    payment_date: datetime
    notes: Optional[str] = None

class PaymentSubmissionCreate(PaymentSubmissionBase):
    pass

class PaymentSubmissionUpdate(BaseModel):
    payment_slip_url: Optional[str] = None
    amount_paid: Optional[str] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None

class PaymentVerificationUpdate(BaseModel):
    status: str = Field(..., description="Status: pending, verified, rejected")
    verification_notes: Optional[str] = None

class PaymentSubmissionResponse(PaymentSubmissionBase):
    id: int
    student_id: int
    status: str
    verification_notes: Optional[str] = None
    submitted_at: datetime
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Student profile info for submission responses
class StudentInfo(BaseModel):
    id: int
    enrollment_number: str
    user_id: int
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True

# Complete response with student info
class PaymentSubmissionWithStudentResponse(PaymentSubmissionResponse):
    student: StudentInfo

    class Config:
        from_attributes = True 