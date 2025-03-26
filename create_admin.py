import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine, Base
from app.models.users import User, UserRole
from app.utils.auth import get_password_hash

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_admin_user(db: Session):
    # Check if admin already exists
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if admin:
        print(f"Admin user already exists: {admin.username}")
        return admin
    
    # Create new admin user
    admin_username = "admin"
    admin_password = "admin123"  # This should be changed after first login!
    admin_email = "admin@example.com"
    
    hashed_password = get_password_hash(admin_password)
    db_admin = User(
        email=admin_email,
        username=admin_username,
        hashed_password=hashed_password,
        role=UserRole.ADMIN,
        first_name="System",
        last_name="Administrator",
        is_active=True
    )
    
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    print(f"Admin user created successfully!")
    print(f"Username: {admin_username}")
    print(f"Password: {admin_password}")
    print("IMPORTANT: Please change the password after first login!")
    
    return db_admin

if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_admin_user(db)
    finally:
        db.close() 