# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

This is a FastAPI + Vue.js web application for transcribing and summarizing meeting audio files. The backend uses AssemblyAI for speech-to-text transcription and OpenAI-compatible models for generating meeting summaries.

**Core Architecture:**
- **Backend**: FastAPI with SQLAlchemy, single-file structure in `backend/main.py`
- **Frontend**: Vue.js 3 with TailwindCSS, component-based architecture
- **Database**: SQLite for development, PostgreSQL for production with optional authentication
- **Audio processing**: Upload → FFmpeg conversion → AssemblyAI transcription → OpenAI summarization
- **Export**: Markdown files with timestamps

## Development Commands

**Backend Development:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend Development:**
```bash
cd frontend
npm install
npm run dev
```

**Production (Docker):**
```bash
docker-compose up -d
```

**Testing:**
```bash
# Backend API test
curl http://localhost:8000/

# Frontend build test
cd frontend && npm run build
```

## Required Environment Variables

```bash
# API Keys (Required)
OPENAI_API_KEY=your_openai_key
ASSEMBLYAI_API_KEY=your_assemblyai_key

# Model Configuration
TEXT_MODEL_NAME=gemini/gemini-2.0-flash
OPENAI_BASE_URL=https://api.openai.com/v1

# Authentication (Development: disable, Production: enable)
DISABLE_AUTH=true  # Set to false for production
JWT_SECRET_KEY=your-secret-key-change-in-production

# Database (Optional - PostgreSQL for production)
DB_NAME=meeting_summarizer
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## Architecture Details

**Backend Structure (`backend/`):**
- `main.py`: FastAPI app with all routes and middleware
- `models.py`: SQLAlchemy database models and session management
- `services.py`: AssemblyAI transcription and OpenAI summarization logic
- `auth.py`: JWT authentication and PostgreSQL user verification
- `database.db`: SQLite database (auto-created in development)

**Frontend Structure (`frontend/src/`):**
- `App.vue`: Main application component with routing logic
- `components/AudioUpload.vue`: File upload and progress tracking
- `components/TranscriptEditor.vue`: Editable transcript with speaker management
- `components/SummaryPanel.vue`: AI summary display and export
- `api.js`: Axios-based API client with authentication handling

**Key API Endpoints:**
- `GET /`: Health check and authentication status
- `POST /auth/login`: User authentication (if enabled)
- `POST /upload`: Audio file upload and transcription
- `GET /transcription/{id}`: Retrieve transcription data
- `POST /summarize/{id}`: Generate AI summary
- `GET /export/{id}`: Download markdown export

## Audio Processing Pipeline

1. **Upload**: Support for MP3, WAV, M4A, and other common formats
2. **Conversion**: FFmpeg processes audio to 16kHz mono MP3
3. **Transcription**: AssemblyAI API with speaker diarization
4. **Editing**: Frontend allows speaker name/info editing
5. **Summarization**: OpenAI-compatible model generates structured summary
6. **Export**: Markdown file with timestamps and speaker attribution

## System Dependencies

- **Backend**: Python 3.12+, ffmpeg for audio conversion
- **Frontend**: Node.js 18+, npm/pnpm for package management
- **Database**: SQLite (development), PostgreSQL (production with auth)
- **Docker**: For containerized deployment

## Authentication Modes

**Development Mode** (`DISABLE_AUTH=true`):
- No login required, direct access to all features
- Uses SQLite database for transcript storage
- Suitable for local development and testing

**Production Mode** (`DISABLE_AUTH=false`):
- PostgreSQL-based authentication using existing `LiteLLM_UserTable`
- SHA256 password hashing with JWT token sessions
- User-specific transcript storage and access control