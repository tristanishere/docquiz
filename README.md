# Document AI Processor

A comprehensive web application that processes various document types and audio files to generate AI-powered summaries and interactive quizzes. Built with FastAPI, modern JavaScript, and a beautiful responsive UI.

## 🚀 Features

### File Processing
- **Document Support**: PDF, Word (.docx, .doc), PowerPoint (.pptx, .ppt)
- **Audio Support**: MP3, WAV, M4A, FLAC, OGG, AAC with automatic transcription
- **Batch Upload**: Upload multiple files simultaneously
- **Drag & Drop**: Intuitive file upload interface

### AI-Powered Analysis
- **Smart Summaries**: Choose from short, medium, or long summaries
- **Interactive Quizzes**: Generate customizable quiz questions (5-25 questions)
- **Content Extraction**: Automatic text extraction from all supported formats
- **Audio Transcription**: Convert speech to text for analysis

### Session Management
- **Save Sessions**: Store processed sessions with custom names
- **History View**: Access all previous sessions
- **Real-time Status**: Monitor processing progress
- **Session Recovery**: Resume work on previous sessions

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite/PostgreSQL**: Database support
- **Python-docx/PyPDF2/python-pptx**: Document processing
- **SpeechRecognition/pydub**: Audio processing and transcription
- **OpenAI API**: AI-powered content generation (optional)

### Frontend
- **Vanilla JavaScript**: Modern ES6+ features
- **Tailwind CSS**: Utility-first CSS framework
- **Font Awesome**: Beautiful icons
- **Responsive Design**: Mobile-first approach

## 📋 Prerequisites

- Python 3.8+
- FFmpeg (for audio processing)
- OpenAI API key (optional, for enhanced AI features)

### FFmpeg Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [FFmpeg official website](https://ffmpeg.org/download.html)

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd document-ai-processor
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application:**
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./document_processor.db

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# File Upload Configuration
MAX_FILE_SIZE=100MB
UPLOAD_DIR=uploads

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### OpenAI API Setup (Optional)

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Add it to your `.env` file
3. The application will automatically use AI-powered summaries and quizzes
4. Without an API key, the application uses intelligent mock responses

## 📖 Usage

### 1. Upload Files
- Drag and drop files or click "Browse Files"
- Supported formats: PDF, Word, PowerPoint, Audio
- Multiple files can be uploaded simultaneously

### 2. Monitor Processing
- Real-time status updates for each file
- Audio files are automatically transcribed
- Processing time depends on file size and type

### 3. Generate Results
- **Summaries**: Choose short, medium, or long length
- **Quizzes**: Select number of questions (5-25)
- Both are generated instantly from processed content

### 4. Save Sessions
- Give your session a memorable name
- Access it later from the History button
- Perfect for ongoing projects or study sessions

## 🔧 API Endpoints

### File Management
- `POST /upload` - Upload multiple files
- `GET /status/{session_id}` - Check processing status
- `GET /session/{session_id}/files` - Get session files

### Content Generation
- `GET /summary/{session_id}` - Generate summary (short/medium/long)
- `GET /quiz/{session_id}` - Generate quiz (5-50 questions)

### Session Management
- `POST /save-session/{session_id}` - Save session with name
- `GET /saved-sessions` - Get all saved sessions

## 🏗️ Project Structure

```
document-ai-processor/
├── main.py                 # FastAPI application entry point
├── models.py              # Database models
├── database.py            # Database configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── services/             # Business logic services
│   ├── __init__.py
│   ├── document_processor.py  # File processing logic
│   ├── ai_service.py          # AI content generation
│   └── file_service.py        # File management
├── templates/            # HTML templates
│   └── index.html       # Main application interface
├── static/              # Static assets
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── app.js       # Frontend application logic
└── uploads/             # File upload directory (auto-created)
```

## 🧪 Testing

### Manual Testing
1. Start the application
2. Upload various file types
3. Test summary generation
4. Test quiz generation
5. Test session saving and history

### File Type Testing
- **PDF**: Text extraction and processing
- **Word**: Document parsing
- **PowerPoint**: Slide content extraction
- **Audio**: Transcription accuracy

## 🚨 Troubleshooting

### Common Issues

**Audio transcription not working:**
- Ensure FFmpeg is installed and accessible
- Check audio file format support
- Verify file isn't corrupted

**File upload errors:**
- Check file size limits
- Verify file format support
- Ensure upload directory has write permissions

**AI features not working:**
- Verify OpenAI API key in `.env`
- Check API quota and billing
- Application falls back to mock responses

**Database errors:**
- Ensure database URL is correct
- Check database permissions
- SQLite file should be writable

### Performance Tips

- Use smaller audio files for faster transcription
- Process large documents in smaller batches
- Monitor database performance for large sessions
- Consider PostgreSQL for production use

## 🔒 Security Considerations

- File upload validation and sanitization
- Session-based access control
- Secure file storage with unique naming
- CORS configuration for production
- Environment variable protection

## 🚀 Deployment

### Production Setup

1. **Use production database:**
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

2. **Set production environment:**
```env
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

3. **Use production server:**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

4. **Set up reverse proxy (nginx):**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- OpenAI for AI capabilities
- Tailwind CSS for the beautiful UI components
- Font Awesome for the icons

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**Happy Document Processing! 🎉**