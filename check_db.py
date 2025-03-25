from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import SQLALCHEMY_DATABASE_URL
from app.models.users import User, Course, CourseWeek, CourseMaterial

# Create database connection
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def print_database_info():
    try:
        print("------- Database Contents -------")
        
        # Count users
        users_count = db.query(User).count()
        print(f"Total Users: {users_count}")
        if users_count > 0:
            users = db.query(User).all()
            print("\nUser Details:")
            for user in users:
                print(f"  - {user.username} ({user.email}): {user.role}")
        
        # Count courses
        courses_count = db.query(Course).count()
        print(f"\nTotal Courses: {courses_count}")
        if courses_count > 0:
            courses = db.query(Course).all()
            print("\nCourse Details:")
            for course in courses:
                print(f"  - {course.title} (ID: {course.id})")
        
        # Count course weeks
        weeks_count = db.query(CourseWeek).count()
        print(f"\nTotal Course Weeks: {weeks_count}")
        if weeks_count > 0:
            weeks = db.query(CourseWeek).all()
            print("\nCourse Week Details:")
            for week in weeks:
                print(f"  - Course ID {week.course_id}: Week {week.week_number} - {week.title}")
        
        # Count course materials
        materials_count = db.query(CourseMaterial).count()
        print(f"\nTotal Course Materials: {materials_count}")
        if materials_count > 0:
            materials = db.query(CourseMaterial).all()
            print("\nCourse Material Details:")
            for material in materials:
                print(f"  - Week ID {material.week_id}: {material.title} ({material.material_type})")
        
        print("\n---------------------------------")
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print_database_info() 