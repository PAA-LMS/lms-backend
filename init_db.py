from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine, Base
from app.models.users import User, LecturerProfile, StudentProfile, Course, CourseWeek, CourseMaterial, UserRole
from app.utils.auth import get_password_hash
import sqlalchemy.exc

print("Attempting to create database tables...")
try:
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
except sqlalchemy.exc.OperationalError as e:
    print(f"Error connecting to MySQL database: {e}")
    print("\nPlease make sure:")
    print("1. XAMPP is installed and MySQL service is running")
    print("2. The database 'lms_db' has been created in phpMyAdmin")
    print("3. The username and password in database.py match your MySQL settings")
    exit(1)

def init_db():
    db = SessionLocal()
    try:
        # Check if we already have course weeks
        course_week_count = db.query(CourseWeek).count()
        
        if course_week_count == 0:
            print("Adding course weeks and materials...")
            
            # Get existing courses
            courses = db.query(Course).all()
            
            if len(courses) > 0:
                # Use the first course (Introduction to Python)
                python_course = db.query(Course).filter(Course.title == "Introduction to Python").first()
                if not python_course and len(courses) > 0:
                    python_course = courses[0]
                
                # Use the second course (Web Development with FastAPI) if available
                fastapi_course = db.query(Course).filter(Course.title == "Web Development with FastAPI").first()
                if not fastapi_course and len(courses) > 1:
                    fastapi_course = courses[1]
                
                if python_course:
                    # Add course weeks to Python course
                    weeks_python = [
                        CourseWeek(
                            course_id=python_course.id,
                            title="Week 1: Python Basics",
                            description="Introduction to Python syntax and basic concepts",
                            week_number=1
                        ),
                        CourseWeek(
                            course_id=python_course.id,
                            title="Week 2: Data Structures",
                            description="Working with lists, dictionaries, and tuples",
                            week_number=2
                        ),
                        CourseWeek(
                            course_id=python_course.id,
                            title="Week 3: Functions",
                            description="Creating and using functions in Python",
                            week_number=3
                        )
                    ]
                    
                    for week in weeks_python:
                        db.add(week)
                    
                    db.commit()
                    
                if fastapi_course:
                    # Add course weeks to FastAPI course
                    weeks_fastapi = [
                        CourseWeek(
                            course_id=fastapi_course.id,
                            title="Week 1: FastAPI Introduction",
                            description="Getting started with FastAPI",
                            week_number=1
                        ),
                        CourseWeek(
                            course_id=fastapi_course.id,
                            title="Week 2: Creating APIs",
                            description="Building your first REST API",
                            week_number=2
                        )
                    ]
                    
                    for week in weeks_fastapi:
                        db.add(week)
                    
                    db.commit()
                
                # Fetch weeks to add materials
                if python_course:
                    python_week1 = db.query(CourseWeek).filter(
                        CourseWeek.course_id == python_course.id,
                        CourseWeek.week_number == 1
                    ).first()
                    
                    python_week2 = db.query(CourseWeek).filter(
                        CourseWeek.course_id == python_course.id,
                        CourseWeek.week_number == 2
                    ).first()
                
                if fastapi_course:
                    fastapi_week1 = db.query(CourseWeek).filter(
                        CourseWeek.course_id == fastapi_course.id,
                        CourseWeek.week_number == 1
                    ).first()
                
                # Add materials to weeks
                materials = []
                
                if python_course and python_week1:
                    materials.append(
                        CourseMaterial(
                            week_id=python_week1.id,
                            title="Python Installation Guide",
                            description="Step-by-step guide to install Python",
                            material_type="drive_url",
                            content="https://drive.google.com/file/example/pythoninstall"
                        )
                    )
                    materials.append(
                        CourseMaterial(
                            week_id=python_week1.id,
                            title="Python Basics Slides",
                            description="Lecture slides covering Python basics",
                            material_type="drive_url",
                            content="https://drive.google.com/file/example/pythonbasics"
                        )
                    )
                
                if python_course and python_week2:
                    materials.append(
                        CourseMaterial(
                            week_id=python_week2.id,
                            title="Data Structures in Python",
                            description="Article about Python data structures",
                            material_type="link",
                            content="https://example.com/python-data-structures"
                        )
                    )
                
                if fastapi_course and fastapi_week1:
                    materials.append(
                        CourseMaterial(
                            week_id=fastapi_week1.id,
                            title="FastAPI Documentation",
                            description="Official FastAPI documentation",
                            material_type="link",
                            content="https://fastapi.tiangolo.com/"
                        )
                    )
                
                for material in materials:
                    db.add(material)
                
                db.commit()
                
                print("Course weeks and materials have been added successfully!")
            else:
                print("No courses found. Please add courses first.")
        else:
            print("Course weeks already exist in the database. Skipping initialization.")
            
        # Original code for creating users if they don't exist
        user_count = db.query(User).count()
        if user_count == 0:
            print("Creating initial users...")
            
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
            
            print("Initial users and courses have been created successfully!")
        else:
            print("Users already exist in the database.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 