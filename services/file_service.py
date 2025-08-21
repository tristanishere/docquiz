import os
import shutil
from typing import List
from fastapi import UploadFile
import uuid

class FileService:
    def __init__(self):
        self.upload_dir = "uploads"
        self.supported_extensions = {
            'pdf': ['.pdf'],
            'docx': ['.docx', '.doc'],
            'pptx': ['.pptx', '.ppt'],
            'audio': ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac']
        }
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def is_valid_file_type(self, filename: str) -> bool:
        """Check if the file type is supported"""
        if not filename:
            return False
        
        file_extension = os.path.splitext(filename.lower())[1]
        
        for extensions in self.supported_extensions.values():
            if file_extension in extensions:
                return True
        
        return False
    
    def get_file_type(self, filename: str) -> str:
        """Get the file type category based on extension"""
        if not filename:
            return "unknown"
        
        file_extension = os.path.splitext(filename.lower())[1]
        
        for file_type, extensions in self.supported_extensions.items():
            if file_extension in extensions:
                return file_type
        
        return "unknown"
    
    async def save_file(self, file: UploadFile, session_id: str) -> str:
        """Save uploaded file to disk"""
        try:
            # Create session directory
            session_dir = os.path.join(self.upload_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(session_dir, unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Error saving file: {str(e)}")
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def cleanup_session_files(self, session_id: str):
        """Clean up all files for a session"""
        try:
            session_dir = os.path.join(self.upload_dir, session_id)
            if os.path.exists(session_dir):
                shutil.rmtree(session_dir)
        except Exception as e:
            print(f"Error cleaning up session files: {e}")
    
    def get_supported_formats(self) -> dict:
        """Get list of supported file formats"""
        return {
            "Documents": {
                "PDF": [".pdf"],
                "Word": [".docx", ".doc"],
                "PowerPoint": [".pptx", ".ppt"]
            },
            "Audio": {
                "Audio Files": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"]
            }
        }