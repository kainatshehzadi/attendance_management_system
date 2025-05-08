from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database URL setup from environment variables (you can change this if needed)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:12345@localhost:5432/attendence")

# Create the database engine
engine = create_engine(DATABASE_URL)
# Create a session local class for the DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create the base class for models
Base = declarative_base()

# Dependency for getting the session (used in API endpoints)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
