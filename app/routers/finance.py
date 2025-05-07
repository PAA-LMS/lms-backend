from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import List, Optional
from ..database.database import get_db
from ..models.finance import PaymentAnnouncement, PaymentSubmission
from ..models.users import User, StudentProfile, UserRole
from ..schemas.finance import (
    PaymentAnnouncementCreate,
    PaymentAnnouncementUpdate,
    PaymentAnnouncementResponse,
    PaymentSubmissionCreate,
    PaymentSubmissionUpdate,
    PaymentSubmissionResponse,
    PaymentVerificationUpdate,
    PaymentSubmissionWithStudentResponse,
    StudentInfo
)
from ..utils.auth import get_current_user

router = APIRouter(
    prefix="/finance",
    tags=["finance"],
    responses={404: {"description": "Not found"}},
)

# Payment Announcements Endpoints

@router.post("/announcements/", response_model=PaymentAnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_payment_announcement(
    announcement: PaymentAnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only lecturers and admins can create payment announcements
    if current_user.role not in [UserRole.LECTURER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers and admins can create payment announcements"
        )
    
    db_announcement = PaymentAnnouncement(
        **announcement.dict(),
        created_by=current_user.id
    )
    
    try:
        db.add(db_announcement)
        db.commit()
        db.refresh(db_announcement)
        return db_announcement
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/announcements/", response_model=List[PaymentAnnouncementResponse])
def get_all_payment_announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        announcements = db.query(PaymentAnnouncement).all()
        return announcements
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/announcements/{announcement_id}", response_model=PaymentAnnouncementResponse)
def get_payment_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        announcement = db.query(PaymentAnnouncement).filter(PaymentAnnouncement.id == announcement_id).first()
        if not announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment announcement not found"
            )
        return announcement
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.put("/announcements/{announcement_id}", response_model=PaymentAnnouncementResponse)
def update_payment_announcement(
    announcement_id: int,
    announcement: PaymentAnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only lecturers and admins can update payment announcements
    if current_user.role not in [UserRole.LECTURER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers and admins can update payment announcements"
        )
    
    try:
        db_announcement = db.query(PaymentAnnouncement).filter(PaymentAnnouncement.id == announcement_id).first()
        if not db_announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment announcement not found"
            )
        
        # Update only provided fields
        update_data = announcement.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_announcement, key, value)
        
        db_announcement.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_announcement)
        return db_announcement
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only lecturers and admins can delete payment announcements
    if current_user.role not in [UserRole.LECTURER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers and admins can delete payment announcements"
        )
    
    try:
        db_announcement = db.query(PaymentAnnouncement).filter(PaymentAnnouncement.id == announcement_id).first()
        if not db_announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment announcement not found"
            )
        
        db.delete(db_announcement)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# Payment Submissions Endpoints

@router.post("/submissions/", response_model=PaymentSubmissionResponse, status_code=status.HTTP_201_CREATED)
def submit_payment(
    submission: PaymentSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only students can submit payments
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can submit payments"
        )
    
    # Get student profile
    student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Verify the announcement exists
    announcement = db.query(PaymentAnnouncement).filter(PaymentAnnouncement.id == submission.announcement_id).first()
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment announcement not found"
        )
    
    # Check if student has already submitted for this announcement
    existing_submission = db.query(PaymentSubmission).filter(
        PaymentSubmission.announcement_id == submission.announcement_id,
        PaymentSubmission.student_id == student_profile.id
    ).first()
    
    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted a payment for this announcement. Please update your existing submission instead."
        )
    
    # Create new submission
    try:
        new_submission = PaymentSubmission(
            **submission.dict(),
            student_id=student_profile.id,
            submitted_at=datetime.utcnow()
        )
        
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
        return new_submission
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/submissions/my", response_model=List[PaymentSubmissionResponse])
def get_my_payment_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only students can view their own submissions
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their own submissions"
        )
    
    # Get student profile
    student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    try:
        submissions = db.query(PaymentSubmission).filter(
            PaymentSubmission.student_id == student_profile.id
        ).all()
        return submissions
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/submissions/announcement/{announcement_id}", response_model=List[PaymentSubmissionWithStudentResponse])
def get_submissions_for_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only lecturers and admins can view submissions for announcements
    if current_user.role not in [UserRole.LECTURER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers and admins can view payment submissions"
        )
    
    # Verify the announcement exists
    announcement = db.query(PaymentAnnouncement).filter(PaymentAnnouncement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment announcement not found"
        )
    
    try:
        # Join with StudentProfile and User to get student information
        submissions_with_student = []
        
        submissions = db.query(PaymentSubmission).filter(
            PaymentSubmission.announcement_id == announcement_id
        ).all()
        
        for submission in submissions:
            # Get student profile and user info
            student_profile = db.query(StudentProfile).filter(
                StudentProfile.id == submission.student_id
            ).first()
            
            user = db.query(User).filter(
                User.id == student_profile.user_id
            ).first()
            
            # Create student info object
            student_info = StudentInfo(
                id=student_profile.id,
                enrollment_number=student_profile.enrollment_number,
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email
            )
            
            # Create submission with student info
            submission_dict = {**submission.__dict__}
            submission_dict["student"] = student_info
            
            submissions_with_student.append(submission_dict)
        
        return submissions_with_student
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.put("/submissions/{submission_id}", response_model=PaymentSubmissionResponse)
def update_payment_submission(
    submission_id: int,
    submission_update: PaymentSubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only students can update their own submissions
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can update their own submissions"
        )
    
    try:
        # Get student profile
        student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if not student_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        
        # Get submission and check if it belongs to the student
        db_submission = db.query(PaymentSubmission).filter(
            PaymentSubmission.id == submission_id,
            PaymentSubmission.student_id == student_profile.id
        ).first()
        
        if not db_submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment submission not found or you don't have permission to update it"
            )
        
        # Only allow updates if the submission is still pending
        if db_submission.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update submission with status '{db_submission.status}'. Only pending submissions can be updated."
            )
        
        # Update fields
        update_data = submission_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_submission, key, value)
        
        db_submission.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_submission)
        return db_submission
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.put("/submissions/{submission_id}/verify", response_model=PaymentSubmissionResponse)
def verify_payment_submission(
    submission_id: int,
    verification: PaymentVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only lecturers and admins can verify payments
    if current_user.role not in [UserRole.LECTURER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers and admins can verify payments"
        )
    
    # Validate status
    if verification.status not in ["pending", "verified", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be one of: pending, verified, rejected"
        )
    
    try:
        # Get submission
        db_submission = db.query(PaymentSubmission).filter(
            PaymentSubmission.id == submission_id
        ).first()
        
        if not db_submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment submission not found"
            )
        
        # Update verification details
        db_submission.status = verification.status
        db_submission.verification_notes = verification.verification_notes
        
        # If status is verified or rejected, update verified_at timestamp
        if verification.status in ["verified", "rejected"]:
            db_submission.verified_at = datetime.utcnow()
        
        db_submission.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_submission)
        return db_submission
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) 