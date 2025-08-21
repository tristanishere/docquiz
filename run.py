#!/usr/bin/env python3
"""
Document AI Processor - Startup Script
This script provides an easy way to run the application with proper configuration.
"""

import os
import sys
import uvicorn
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import fastapi
        import sqlalchemy
        import PyPDF2
        import docx
        import pptx
        import speech_recognition
        import pydub
        print("✅ All required dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_ffmpeg():
    """Check if FFmpeg is available for audio processing"""
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg is available for audio processing")
            return True
        else:
            print("⚠️  FFmpeg may not be properly installed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  FFmpeg not found. Audio transcription will not work.")
        print("   Install FFmpeg for audio support:")
        print("   - Ubuntu/Debian: sudo apt install ffmpeg")
        print("   - macOS: brew install ffmpeg")
        print("   - Windows: Download from https://ffmpeg.org/")
        return False

def setup_environment():
    """Set up environment variables and directories"""
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    print(f"✅ Uploads directory: {uploads_dir.absolute()}")
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Using default configuration.")
        print("   Copy .env.example to .env and customize as needed.")
    else:
        print("✅ Environment configuration loaded")
    
    # Set default values
    os.environ.setdefault("DATABASE_URL", "sqlite:///./document_processor.db")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8000")
    os.environ.setdefault("DEBUG", "true")

def main():
    """Main startup function"""
    print("🚀 Starting Document AI Processor...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check FFmpeg
    check_ffmpeg()
    
    # Setup environment
    setup_environment()
    
    print("\n📋 Configuration:")
    print(f"   Host: {os.environ.get('HOST', '0.0.0.0')}")
    print(f"   Port: {os.environ.get('PORT', '8000')}")
    print(f"   Database: {os.environ.get('DATABASE_URL', 'sqlite:///./document_processor.db')}")
    print(f"   Debug: {os.environ.get('DEBUG', 'true')}")
    
    # Check OpenAI API key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        print("✅ OpenAI API key configured")
    else:
        print("⚠️  No OpenAI API key found. Using mock AI responses.")
        print("   Set OPENAI_API_KEY in .env for enhanced AI features.")
    
    print("\n🌐 Starting server...")
    print("   Access the application at: http://localhost:8000")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the server
        uvicorn.run(
            "main:app",
            host=os.environ.get("HOST", "0.0.0.0"),
            port=int(os.environ.get("PORT", "8000")),
            reload=os.environ.get("DEBUG", "true").lower() == "true",
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()