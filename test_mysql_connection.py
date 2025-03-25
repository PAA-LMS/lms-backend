from sqlalchemy import create_engine, text
from app.database.database import SQLALCHEMY_DATABASE_URL

def test_connection():
    try:
        # Create a test engine
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("MySQL connection successful!")
            
            # Test query to fetch users
            users = connection.execute(text("SELECT id, username, email, role FROM users")).fetchall()
            print(f"\nFound {len(users)} users:")
            for user in users:
                print(f"  - {user[1]} ({user[2]}): {user[3]}")
                
            # Test query to fetch courses
            courses = connection.execute(text("SELECT id, title FROM courses")).fetchall()
            print(f"\nFound {len(courses)} courses:")
            for course in courses:
                print(f"  - {course[1]} (ID: {course[0]})")
            
            # Test query to check course weeks
            weeks = connection.execute(text(
                "SELECT cw.id, c.title, cw.week_number, cw.title " +
                "FROM course_weeks cw " +
                "JOIN courses c ON cw.course_id = c.id " +
                "ORDER BY c.id, cw.week_number"
            )).fetchall()
            print(f"\nFound {len(weeks)} course weeks:")
            for week in weeks:
                print(f"  - Course '{week[1]}': Week {week[2]} - {week[3]}")
                
            # Test query to check course materials
            materials = connection.execute(text(
                "SELECT cm.id, cw.title, c.title, cm.title, cm.material_type " +
                "FROM course_materials cm " +
                "JOIN course_weeks cw ON cm.week_id = cw.id " +
                "JOIN courses c ON cw.course_id = c.id " +
                "ORDER BY c.id, cw.week_number"
            )).fetchall()
            print(f"\nFound {len(materials)} course materials:")
            for material in materials:
                print(f"  - Course '{material[2]}', Week '{material[1]}': {material[3]} ({material[4]})")
                
        return True
    except Exception as e:
        print(f"MySQL connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection() 