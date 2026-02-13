# DocuChat AI

Document question-answering powered by RAG (Retrieval Augmented Generation).

## 🚀 Free Cloud Deployment Available

Deploy for **$0/month** with **built-in protection** to ensure you never pay:

- ✅ **Cloudflare Pages** (frontend) - Unlimited bandwidth, always free
- ✅ **Google Cloud Run** (backend) - 2M requests/month free, never sleeps
- ✅ **Automatic cutoff** at 2M requests - impossible to exceed free tier
- ✅ **One-command deployment** - See [QUICKDEPLOY.md](QUICKDEPLOY.md)

**[📖 Quick Deploy Guide](QUICKDEPLOY.md)** | **[🛡️ Free Tier Protection Details](FREE_TIER_PROTECTION.md)**

---

## Tech Stack

**Frontend:** React 18, Vite, TailwindCSS, shadcn/ui, Framer Motion  
**Backend:** FastAPI, PostgreSQL, LanceDB, LangChain, Groq (Llama 3.3), Unstructured  
**CI/CD:** GitHub Actions

## Project Structure

```
rag-app/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/                # Config, database, exceptions
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── main.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom hooks
│   │   └── services/            # API client
│   ├── package.json
│   └── vite.config.js
└── .github/workflows/ci.yml     # CI/CD pipeline
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Groq API Key (https://console.groq.com)

### Installation

**1. Backend Setup**

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env`:
```env
DATABASE_URL=postgresql://raguser:ragpassword@localhost:5432/ragdb
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_generated_secret_key
```

**2. Frontend Setup**

```bash
cd frontend
npm install
cp .env.example .env
```

**3. Start Database**

```bash
docker-compose up -d
```

**4. Run Application**

Backend:
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

Access the application:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Note:** Environment variable changes require a backend restart.

## Configuration

### Environment Variables

**Backend (.env)**

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | Required |
| GROQ_API_KEY | Groq API key | Required |
| SECRET_KEY | Application secret key | Required |
| BACKEND_CORS_ORIGINS | Allowed CORS origins | ["http://localhost:5173"] |
| UPLOAD_DIR | File upload directory | ./uploads |
| MAX_UPLOAD_SIZE | Max file size in bytes | 10485760 (10MB) |
| CHROMA_PERSIST_DIRECTORY | Vector store path | ./chroma_data |
| MODEL_NAME | LLM model | llama-3.3-70b-versatile |
| TEMPERATURE | LLM temperature | 0.7 |
| MAX_TOKENS | Max response tokens | 1024 |

**Frontend (.env)**

| Variable | Description |
|----------|-------------|
| VITE_API_URL | Backend API URL |

### Getting Groq API Key

1. Sign up at https://console.groq.com
2. Create an API key
3. Add to `backend/.env`

## API Endpoints

**Documents**
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/status/{id}` - Check processing status
- `GET /api/v1/documents/` - List all documents
- `DELETE /api/v1/documents/{id}` - Delete document

**Chat**
- `POST /api/v1/chat/ask` - Ask question about document
- `GET /api/v1/chat/history/{session_id}` - Get chat history

**Health**
- `GET /api/v1/health` - Health check

## Features

- Upload PDF, DOC, DOCX, TXT files
- Ask questions about uploaded documents
- Context-aware responses with source citations
- Chat history and session management
- Light/dark mode
- Responsive design

## Development

### Code Style

**Python:** Black formatter (88 char), isort, Pylint, type hints  
**JavaScript:** ESLint with React rules

## CI/CD Pipeline

GitHub Actions runs on push/PR:

- Backend: Pylint
- Frontend: ESLint, build check

## Troubleshooting

**Database connection errors:**
```bash
docker-compose restart postgres
docker-compose logs postgres
```

**PostCSS ES module error:**
```bash
cd frontend
mv postcss.config.js postcss.config.cjs
```

**Missing sentence-transformers:**
```bash
cd backend
pip install sentence-transformers
```

**Model decommissioned error:**
Ensure `.env` uses `MODEL_NAME=llama-3.3-70b-versatile`, then restart backend.

**CORS errors:**  
Verify `BACKEND_CORS_ORIGINS` in `.env` includes frontend URL.

## Production Deployment

### Cloud Deployment (Free Tier)

**Quick Deploy:**
```powershell
# Windows
.\deploy-backend.ps1

# Mac/Linux
chmod +x deploy-backend.sh
./deploy-backend.sh
```

See [QUICKDEPLOY.md](QUICKDEPLOY.md) for complete instructions.

**Includes:**
- 🛡️ Built-in rate limiting (2M requests/month)
- ✅ Resource limits (max 10 instances, 80 concurrency)
- ✅ Automatic monthly reset
- ✅ Budget protection (never enter paid tier)

**Deployment targets:**
- **Backend:** Google Cloud Run (free, never sleeps)
- **Frontend:** Cloudflare Pages (free, unlimited bandwidth)

**Requirements:**
- Google Cloud account (free tier)
- Cloudflare account (free)
- Groq API key

### Self-Hosted Deployment

For self-hosting:
- Set strong `SECRET_KEY`
- Configure production database (PostgreSQL recommended)
- Update `BACKEND_CORS_ORIGINS`
- Set up reverse proxy with HTTPS (nginx/Caddy)
- Configure persistent file storage
- Set up backup strategy for uploads and vector database

## License

MIT
