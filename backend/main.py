from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import tempfile
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import get_db, Transcription
from services import convert_to_mp3, transcribe_audio, summarize_meeting, save_summary_as_markdown

app = FastAPI(title="Meeting Summarizer API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Meeting Summarizer API", "version": "1.0.0"}

@app.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and transcribe audio file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            content = await file.read()
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    
    print("🚀 Starting Meeting Summarizer API...")
    print("📋 Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
    finally:
        print("👋 Meeting Summarizer API shutdown complete")