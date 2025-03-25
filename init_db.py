from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine, Base
from app.models.users import User, LecturerProfile, StudentProfile, Course, UserRole
from app.utils.auth import get_password_hash

# Create database tables
Base.metadata.create_all(bind=engine)

def init_db():
    db = SessionLocal()
    try:
        # Check if we already have users
        user_count = db.query(User).count()
        if user_count == 0:
            print("Creating initial test data...")
            
            # Create a lecturer
            lecturer = User(
                email="lecturer@example.com",
                username="lecturer",
                hashed_password=get_password_hash("password123"),
                role=UserRole.LECTURER,
                first_name="John",
                last_name="Doe",
                is_active=True
            )
            db.add(lecturer)
            db.commit()
            db.refresh(lecturer)
            
            # Create lecturer profile
            lecturer_profile = LecturerProfile(
                user_id=lecturer.id,
                department="Computer Science",
                bio="Experienced professor in software engineering",
                qualification="PhD in Computer Science"
            )
            db.add(lecturer_profile)
            db.commit()
            db.refresh(lecturer_profile)
            
            # Create a student
            student = User(
                email="student@example.com",
                username="student",
                hashed_password=get_password_hash("password123"),
                role=UserRole.STUDENT,
                first_name="Jane",
                last_name="Smith",
                is_active=True
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            
            # Create student profile
            student_profile = StudentProfile(
                user_id=student.id,
                enrollment_number="ST12345",
                semester=3,
                program="Computer Science"
            )
            db.add(student_profile)
            db.commit()
            db.refresh(student_profile)
            
            # Create some courses
            course1 = Course(
                title="Introduction to Python",
                description="Learn the basics of Python programming language",
                lecturer_id=lecturer_profile.id
            )
            
            course2 = Course(
                title="Web Development with FastAPI",
                description="Building modern APIs with FastAPI framework",
                lecturer_id=lecturer_profile.id
            )
            
            db.add(course1)
            db.add(course2)
            db.commit()
            
            print("Test data has been created successfully!")
        else:
            print("Database already contains data. Skipping initialization.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 