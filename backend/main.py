from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import tempfile
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import get_db, Transcription
from services import convert_to_mp3, transcribe_audio, summarize_meeting, save_summary_as_markdown
from auth import verify_user, create_access_token, verify_token

app = FastAPI(title="Summeet API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models for authentication
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_email: str

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from JWT token"""
    token = credentials.credentials
    user_email = verify_token(token)
    if not user_email:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_email

@app.get("/")
async def root():
    return {"message": "Summeet API", "version": "1.0.0"}

@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    try:
        # Verify user credentials
        if not verify_user(request.email, request.password):
            raise HTTPException(
                status_code=401, 
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": request.email},
            expires_delta=timedelta(minutes=30)
        )
        
        return LoginResponse(
            access_token=access_token,
            user_email=request.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Upload and transcribe audio file"""
    try:
        # Save uploaded file temporarily and check size
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            content = await file.read()
            
            # Check file size (limit: 100MB)
            MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="File too large. Maximum size is 100MB.")
            
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Convert to MP3
        mp3_path = convert_to_mp3(tmp_file_path)
        
        # Transcribe audio
        transcript_data = transcribe_audio(mp3_path)
        
        # Save to database
        transcription = Transcription(
            filename=file.filename,
            transcript=transcript_data["text"],
            speakers=transcript_data["speakers"]
        )
        db.add(transcription)
        db.commit()
        db.refresh(transcription)
        
        # Cleanup temporary files
        os.unlink(tmp_file_path)
        os.unlink(mp3_path)
        
        return {
            "id": transcription.id,
            "filename": transcription.filename,
            "transcript": transcription.transcript,
            "speakers": transcription.speakers,
            "created_at": transcription.created_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DirectTranscriptRequest(BaseModel):
    filename: str
    transcript: str
    speakers: str = "[]"

@app.post("/transcript")
async def save_direct_transcript(
    request: DirectTranscriptRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Save direct transcript input to database"""
    try:
        # Save to database
        transcription = Transcription(
            filename=request.filename,
            transcript=request.transcript,
            speakers=request.speakers
        )
        db.add(transcription)
        db.commit()
        db.refresh(transcription)
        
        return {
            "id": transcription.id,
            "filename": transcription.filename,
            "transcript": transcription.transcript,
            "speakers": transcription.speakers,
            "created_at": transcription.created_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transcription/{transcription_id}")
async def get_transcription(
    transcription_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get transcription by ID"""
    transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return {
        "id": transcription.id,
        "filename": transcription.filename,
        "transcript": transcription.transcript,
        "speakers": transcription.speakers,
        "summary": transcription.summary,
        "created_at": transcription.created_at
    }

@app.post("/summarize/{transcription_id}")
async def create_summary(
    transcription_id: int,
    language: str = "en", 
    temperature: float = 0.8,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Generate summary for transcription"""
    transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    try:
        # Parse speakers if available
        speaker_table = None
        if transcription.speakers:
            try:
                import json
                speakers_data = json.loads(transcription.speakers)
                # Convert to format expected by summarize_meeting
                speaker_table = [[s.get('speaker', 'Unknown'), s.get('description', '')] for s in speakers_data]
            except json.JSONDecodeError:
                pass
        
        # Generate summary with language and temperature parameters
        summary = summarize_meeting(
            transcription.transcript, 
            speaker_table=speaker_table,
            system_prompt_language=language,
            temperature=temperature
        )
        
        # Update database
        transcription.summary = summary
        db.commit()
        
        return {"summary": summary}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/{transcription_id}")
async def export_markdown(
    transcription_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Export transcription as markdown file"""
    transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    try:
        # Generate markdown file
        markdown_path = save_summary_as_markdown(
            transcription.transcript,
            transcription.summary or "",
            transcription.filename or f"meeting_{transcription.id}"
        )
        
        return FileResponse(
            markdown_path,
            media_type='text/markdown',
            filename=f"{transcription.filename or f'meeting_{transcription.id}'}_summary.md"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def signal_handler(sig, frame):
    """Handle SIGINT (Ctrl+C) and SIGTERM signals"""
    print("\n🛑 Received shutdown signal. Gracefully shutting down...")
    sys.exit(0)

if __name__ == "__main__":
    import uvicorn
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Summeet API...")
    print("📋 Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
    finally:
        print("👋 Summeet API shutdown complete")