from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Comment out SQLite configuration
# SQLALCHEMY_DATABASE_URL = "sqlite:///./lms.db"

# MySQL configuration with XAMPP
# Default XAMPP MySQL credentials (username: root, password: empty)
# You can change these as needed
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/lms_db"

# Remove SQLite-specific connect_args for MySQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 