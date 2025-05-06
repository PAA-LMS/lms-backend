from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine, Base
import sqlalchemy.exc

def reset_database():
    print("Dropping all database tables...")
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped successfully!")
        
        # Recreate all tables
        print("Recreating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables recreated successfully!")
        
    except sqlalchemy.exc.OperationalError as e:
        print(f"Error connecting to database: {e}")
        print("\nPlease make sure:")
        print("1. XAMPP is installed and MySQL service is running")
        print("2. The database 'lms_db' has been created in phpMyAdmin")
        print("3. The username and password in database.py match your MySQL settings")
        exit(1)

if __name__ == "__main__":
    reset_database()
    print("\nDatabase has been reset successfully!")
    print("Now you can run 'python init_db.py' to initialize the database with sample data.") 