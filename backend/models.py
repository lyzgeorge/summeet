from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Get data directory from environment variable, default to /app/data
DATA_DIR = os.getenv("DATA_DIR", "/app/data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# SQLite database configuration
DATABASE_URL = f"sqlite:///{DATA_DIR}/database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    transcript = Column(Text)
    speakers = Column(Text)  # JSON string
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()