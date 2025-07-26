# Summeet 🎙️

**Turn meeting recordings into actionable summaries in minutes, not hours.**

Stop manually transcribing hours of meetings. Summeet uses AI to automatically transcribe audio files and generate structured summaries with speaker identification and key action items.

> 🎁 **Free to start**: Use AssemblyAI's free tier (up to 5 hours/month) and any OpenAI-compatible model including free options like Groq, DeepSeek, or local models.

![Summeet Interface](screenshots/1-mainpage.jpeg)

## ✨ What it does

📁 **Upload audio** → 🤖 **AI transcribes** → ✏️ **Edit & label speakers** → 📋 **Get summary** → 📄 **Export markdown**

- **Drag & drop** audio files (MP3, WAV, M4A, etc.)
- **Automatic transcription** with speaker detection
- **Edit transcripts** and add speaker names/roles  
- **AI-powered summaries** with action items and key points
- **Export** clean markdown files for sharing

<div align="center">
  <img src="screenshots/2-editspeaker.jpeg" width="45%" />
  <img src="screenshots/3-editsummary.jpeg" width="45%" />
</div>

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and start
git clone https://github.com/lyzgeorge/summeet.git
cd summeet
cp env.example .env

# Add your API keys to .env
# OPENAI_API_KEY=your_key_here
# ASSEMBLYAI_API_KEY=your_key_here

# Run with Docker
docker compose -f docker-compose.simple.yml up -d

# Open http://localhost:3000
```

### Option 2: Development

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install && npm run dev
```

## 💰 Cost-Effective Setup

### Free Tier Options:
- **AssemblyAI**: 5 hours free transcription/month
- **OpenAI alternatives**: Use Groq, DeepSeek, or local models
- **Hosting**: Deploy on your own server or free tiers

### Paid Scaling:
- **AssemblyAI**: $0.37/hour for additional transcription
- **OpenAI**: ~$0.01 per summary with GPT-4o-mini

## ⚙️ Configuration

Create `.env` file:

```bash
# Required
OPENAI_API_KEY=your_openai_key
ASSEMBLYAI_API_KEY=your_assemblyai_key

# Optional: Use alternative providers
OPENAI_BASE_URL=https://api.groq.com/openai/v1  # Groq (free tier)
# OPENAI_BASE_URL=https://api.deepseek.com      # DeepSeek (cheap)
# OPENAI_BASE_URL=http://localhost:1234/v1      # Local model

TEXT_MODEL_NAME=llama-3.1-8b-instant  # For Groq
# TEXT_MODEL_NAME=deepseek-chat        # For DeepSeek
# TEXT_MODEL_NAME=gpt-4o-mini         # For OpenAI
```

## 📸 Screenshots

| Main Interface | Summary Export |
|---|---|
| ![Upload](screenshots/1-mainpage.jpeg) | ![Export](screenshots/4-viewexport.jpeg) |

## 🛠️ Technical Details

**Stack**: FastAPI + Vue.js + SQLite + Docker  
**AI Services**: AssemblyAI (transcription) + OpenAI-compatible APIs (summarization)  
**Deployment**: Single container, runs anywhere

### API Endpoints
- `POST /upload` - Upload and transcribe audio
- `GET /transcription/{id}` - Get transcription  
- `POST /summarize/{id}` - Generate summary
- `GET /export/{id}` - Download markdown

### Supported Formats
MP3, WAV, M4A, FLAC, OGG (auto-converted with FFmpeg)

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - feel free to use this commercially or personally.

## 🔗 Links

- **Issues**: [Report bugs](https://github.com/lyzgeorge/summeet/issues)
- **Discussions**: [Ask questions](https://github.com/lyzgeorge/summeet/discussions)

---

**⭐ Star this repo if it saves you time transcribing meetings!**