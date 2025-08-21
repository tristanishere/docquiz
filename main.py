from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from typing import List, Optional
import os
from datetime import datetime
import uuid

from models import *
from database import engine, SessionLocal
from services.document_processor import DocumentProcessor
from services.ai_service import AIService
from services.file_service import FileService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Document AI Processor", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize services
document_processor = DocumentProcessor()
ai_service = AIService()
file_service = FileService()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple files for processing"""
    try:
        session_id = str(uuid.uuid4())
        uploaded_files = []
        
        for file in files:
            # Validate file type
            if not file_service.is_valid_file_type(file.filename):
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
            
            # Save file
            file_path = await file_service.save_file(file, session_id)
            
            # Create file record
            db_file = FileRecord(
                session_id=session_id,
                filename=file.filename,
                file_path=file_path,
                file_type=file_service.get_file_type(file.filename),
                upload_time=datetime.utcnow()
            )
            db.add(db_file)
            uploaded_files.append(db_file)
        
        db.commit()
        
        # Process files asynchronously
        document_processor.process_files_async(session_id, uploaded_files)
        
        return {
            "session_id": session_id,
            "message": "Files uploaded successfully",
            "files": [{"filename": f.filename, "file_type": f.file_type} for f in uploaded_files]
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{session_id}")
async def get_processing_status(session_id: str, db: Session = Depends(get_db)):
    """Get the processing status of uploaded files"""
    files = db.query(FileRecord).filter(FileRecord.session_id == session_id).all()
    
    if not files:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if processing is complete
    all_processed = all(f.processing_status == "completed" for f in files)
    
    return {
        "session_id": session_id,
        "status": "completed" if all_processed else "processing",
        "files": [
            {
                "filename": f.filename,
                "file_type": f.file_type,
                "status": f.processing_status,
                "upload_time": f.upload_time.isoformat()
            } for f in files
        ]
    }

@app.get("/summary/{session_id}")
async def get_summary(
    session_id: str,
    summary_type: str = "medium",  # short, medium, long
    db: Session = Depends(get_db)
):
    """Get summary of processed documents"""
    if summary_type not in ["short", "medium", "long"]:
        raise HTTPException(status_code=400, detail="Invalid summary type")
    
    # Get processed content
    files = db.query(FileRecord).filter(FileRecord.session_id == session_id).all()
    
    if not files:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if all files are processed
    if not all(f.processing_status == "completed" for f in files):
        raise HTTPException(status_code=400, detail="Files still being processed")
    
    # Get or generate summary
    summary = db.query(Summary).filter(
        Summary.session_id == session_id,
        Summary.summary_type == summary_type
    ).first()
    
    if not summary:
        # Generate summary
        content = []
        for file in files:
            if file.extracted_text:
                content.append(file.extracted_text)
        
        summary_text = ai_service.generate_summary(content, summary_type)
        
        summary = Summary(
            session_id=session_id,
            summary_type=summary_type,
            content=summary_text,
            created_at=datetime.utcnow()
        )
        db.add(summary)
        db.commit()
    
    return {
        "session_id": session_id,
        "summary_type": summary_type,
        "content": summary.content,
        "created_at": summary.created_at.isoformat()
    }

@app.get("/quiz/{session_id}")
async def get_quiz(
    session_id: str,
    question_count: int = 10,
    db: Session = Depends(get_db)
):
    """Get quiz questions for processed documents"""
    if question_count < 5 or question_count > 50:
        raise HTTPException(status_code=400, detail="Question count must be between 5 and 50")
    
    # Get processed content
    files = db.query(FileRecord).filter(FileRecord.session_id == session_id).all()
    
    if not files:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if all files are processed
    if not all(f.processing_status == "completed" for f in files):
        raise HTTPException(status_code=400, detail="Files still being processed")
    
    # Get or generate quiz
    quiz = db.query(Quiz).filter(
        Quiz.session_id == session_id,
        Quiz.question_count == question_count
    ).first()
    
    if not quiz:
        # Generate quiz
        content = []
        for file in files:
            if file.extracted_text:
                content.append(file.extracted_text)
        
        quiz_data = ai_service.generate_quiz(content, question_count)
        
        quiz = Quiz(
            session_id=session_id,
            question_count=question_count,
            questions=quiz_data,
            created_at=datetime.utcnow()
        )
        db.add(quiz)
        db.commit()
    
    return {
        "session_id": session_id,
        "question_count": question_count,
        "questions": quiz.questions,
        "created_at": quiz.created_at.isoformat()
    }

@app.post("/save-session/{session_id}")
async def save_session(
    session_id: str,
    session_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Save a session for later access"""
    # Check if session exists
    files = db.query(FileRecord).filter(FileRecord.session_id == session_id).all()
    
    if not files:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Create or update saved session
    saved_session = db.query(SavedSession).filter(SavedSession.session_id == session_id).first()
    
    if saved_session:
        saved_session.session_name = session_name
        saved_session.updated_at = datetime.utcnow()
    else:
        saved_session = SavedSession(
            session_id=session_id,
            session_name=session_name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(saved_session)
    
    db.commit()
    
    return {
        "message": "Session saved successfully",
        "session_id": session_id,
        "session_name": session_name
    }

@app.get("/saved-sessions")
async def get_saved_sessions(db: Session = Depends(get_db)):
    """Get all saved sessions"""
    saved_sessions = db.query(SavedSession).order_by(SavedSession.updated_at.desc()).all()
    
    return [
        {
            "session_id": s.session_id,
            "session_name": s.session_name,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat()
        } for s in saved_sessions
    ]

@app.get("/session/{session_id}/files")
async def get_session_files(session_id: str, db: Session = Depends(get_db)):
    """Get all files for a specific session"""
    files = db.query(FileRecord).filter(FileRecord.session_id == session_id).all()
    
    if not files:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return [
        {
            "filename": f.filename,
            "file_type": f.file_type,
            "processing_status": f.processing_status,
            "upload_time": f.upload_time.isoformat(),
            "file_size": f.file_size
        } for f in files
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)