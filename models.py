from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime

Base = declarative_base()

class FileRecord(Base):
    __tablename__ = "file_records"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, pptx, docx, audio
    file_size = Column(Integer)
    upload_time = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    extracted_text = Column(Text)
    processing_error = Column(Text)

class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    summary_type = Column(String, nullable=False)  # short, medium, long
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    question_count = Column(Integer, nullable=False)
    questions = Column(JSON, nullable=False)  # Store quiz questions as JSON
    created_at = Column(DateTime, default=datetime.utcnow)

class SavedSession(Base):
    __tablename__ = "saved_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False, unique=True)
    session_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)