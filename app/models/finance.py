from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.database import Base

class PaymentAnnouncement(Base):
    __tablename__ = "payment_announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(String(50), nullable=False)  # Amount to be paid
    payment_details = Column(Text, nullable=False)  # Bank details or payment instructions
    due_date = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    submissions = relationship("PaymentSubmission", back_populates="announcement")

class PaymentSubmission(Base):
    __tablename__ = "payment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    announcement_id = Column(Integer, ForeignKey("payment_announcements.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    payment_slip_url = Column(String(500), nullable=False)  # Google Drive URL for the payment slip
    amount_paid = Column(String(50), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")  # pending, verified, rejected
    notes = Column(Text, nullable=True)  # Additional notes from student
    verification_notes = Column(Text, nullable=True)  # Notes from lecturer during verification
    submitted_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    announcement = relationship("PaymentAnnouncement", back_populates="submissions")
    student = relationship("StudentProfile", back_populates="payment_submissions") 