# Summeet

🎙️ **Open-source AI-powered meeting transcription and summarization tool**

Transform your audio recordings into structured meeting summaries with automatic transcription, speaker identification, and intelligent summarization using state-of-the-art AI models.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Vue.js 3](https://img.shields.io/badge/vue.js-3-green.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## ✨ Features

- 🎙️ **Audio Transcription**: Accurate speech-to-text using AssemblyAI
- 👥 **Speaker Diarization**: Automatic speaker identification and labeling
- 🤖 **AI Summarization**: Intelligent meeting summaries using OpenAI-compatible models
- ✏️ **Editable Transcripts**: Review and edit transcriptions before summarizing
- 📁 **Multiple Input Methods**: Upload audio files or paste existing transcripts
- 📄 **Export Options**: Download formatted Markdown summaries
- 🎨 **Modern Interface**: Clean, responsive Vue.js frontend with Tailwind CSS
- 🐳 **Docker Ready**: Single-container deployment
- 🔓 **No Authentication**: Simple, secure, privacy-focused

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lyzgeorge/summeet.git
   cd summeet
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Start the application**:
   ```bash
   docker compose -f docker-compose.simple.yml up -d
   ```

4. **Access the application**:
   - Open http://localhost:3000 in your browser

### Option 2: Development Setup

1. **Backend setup**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

2. **Frontend setup** (in a new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## ⚙️ Configuration

### Required Environment Variables

Create a `.env` file with your API keys:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# Optional: Model Configuration
TEXT_MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Supported Audio Formats

- MP3, WAV, M4A, FLAC, OGG
- Automatic format conversion using FFmpeg
- Max file size: Limited by your hosting environment

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.12+
- **Database**: SQLite (simple, file-based)
- **Audio Processing**: FFmpeg for format conversion
- **AI Services**: AssemblyAI (transcription) + OpenAI-compatible APIs (summarization)

### Frontend (Vue.js)
- **Framework**: Vue.js 3 with Composition API
- **Styling**: Tailwind CSS for modern, responsive design
- **Components**: Modular, reusable Vue components
- **API Client**: Axios for HTTP requests

### Single Container Deployment
- **Web Server**: Nginx serves frontend static files
- **API Proxy**: Nginx proxies `/api/*` requests to FastAPI backend
- **Process Management**: Both services run in a single container

## 📚 API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

- `POST /upload` - Upload and transcribe audio files
- `POST /transcript` - Save direct transcript input
- `GET /transcription/{id}` - Retrieve transcription data
- `POST /summarize/{id}` - Generate AI summary
- `GET /export/{id}` - Download Markdown export

## 🔧 Development

### Project Structure

```
summeet/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application file
│   ├── models.py           # Database models
│   ├── services.py         # AI service integrations
│   └── requirements.txt    # Python dependencies
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── App.vue        # Main app component
│   │   └── main.js        # App entry point
│   └── package.json       # Node dependencies
├── Dockerfile             # Single-container build
├── docker-compose.simple.yml  # Simple deployment
└── README.md
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm run test
```

## 🐳 Deployment

### Production Deployment

1. **Set up environment**:
   ```bash
   cp env.example .env
   # Configure production API keys
   ```

2. **Deploy with Docker**:
   ```bash
   docker compose -f docker-compose.simple.yml up -d
   ```

3. **Access your application**:
   - The app will be available on port 3000
   - Consider setting up a reverse proxy (nginx/traefik) for SSL

### Resource Requirements

- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 10GB for application + space for uploaded audio files
- **CPU**: 2 cores minimum for concurrent processing

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork and clone the repository
2. Set up both backend and frontend environments
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [AssemblyAI](https://www.assemblyai.com/) for speech-to-text API
- [OpenAI](https://openai.com/) for AI summarization models
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Vue.js](https://vuejs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/lyzgeorge/summeet/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/lyzgeorge/summeet/discussions)
- 📧 **Security Issues**: Report privately via email

---

**Star ⭐ this repo if you find it helpful!**