# DocuChat AI

A production-ready Retrieval Augmented Generation (RAG) application for document question-answering using AI.

## Tech Stack

**Frontend:** React 18, Vite, JavaScript, TailwindCSS, shadcn/ui, Framer Motion  
**Backend:** FastAPI, PostgreSQL, LanceDB, LangChain, Groq (Llama 3.3), Unstructured  
**Testing:** pytest, Vitest, 80%+ coverage requirement  
**CI/CD:** GitHub Actions with automated testing and linting

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
│   ├── tests/                   # Backend tests
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom hooks
│   │   ├── services/            # API client
│   │   └── test/                # Frontend tests
│   ├── package.json
│   └── vite.config.js
└── .github/workflows/ci.yml     # CI/CD pipeline
```

## Quick Start

### Prerequisites

- Python 3.11+ or 3.12+
- Node.js 18+
- Docker & Docker Compose
- Groq API Key (free at https://console.groq.com)

**Note:** Python 3.12 users will automatically get updated dependencies (langchain 0.3+, unstructured 0.17+).

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

**Important:** After changing `.env` files, restart the backend server (Ctrl+C then restart). Auto-reload only works for code changes, not environment variables.

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

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

1. Visit https://console.groq.com
2. Sign up for free account
3. Navigate to API Keys
4. Create and copy key
5. Add to `backend/.env`

Free tier: 14,400 requests/day, 300+ tokens/sec

## Testing

### Backend

```bash
cd backend
pytest --cov=app --cov-report=html --cov-report=term-missing
pylint app --max-line-length=88
```

### Frontend

```bash
cd frontend
npm test
npm run test:coverage
npm run lint
```

**Coverage requirement:** 80% minimum (enforced in CI/CD)

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

**Document Processing**
- Supports PDF, DOC, DOCX, TXT
- Drag-and-drop upload
- Real-time processing status
- Background processing with status tracking

**Chat Interface**
- Context-aware question answering
- Source citations
- Persistent chat history
- Session management

**UI/UX**
- Light/dark mode
- Smooth animations
- Responsive design
- Accessible components

## Development

### Code Style

**Python**
- Black formatter (88 char line length)
- isort for imports
- Pylint for linting
- Type hints required

**JavaScript**
- ESLint with React rules
- Consistent component patterns
- Proper hook usage

### SOLID Principles

- **Single Responsibility:** Each service handles one concern
- **Open/Closed:** Services extend without modification
- **Liskov Substitution:** Abstract base configurations
- **Interface Segregation:** Focused API endpoints
- **Dependency Inversion:** Dependency injection pattern

### Commit Conventions

```
feat: add document deletion
fix: resolve upload timeout issue
docs: update README
test: add chat service tests
```

## CI/CD Pipeline

GitHub Actions runs on every push and PR:

1. **Backend Tests**
   - pytest with 80% coverage check
   - Pylint code quality check
   - Database connectivity test

2. **Frontend Tests**
   - Vitest with 80% coverage check
   - ESLint validation
   - Build verification

**PR Requirements:**
- All tests pass
- Coverage ≥ 80%
- No linting errors

## Troubleshooting

**Database connection errors:**
```bash
docker-compose ps
docker-compose restart postgres
docker-compose logs postgres
```

**Module import errors:**
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

**PostCSS ES module error:**
If you see "module is not defined in ES module scope":
```bash
cd frontend
mv postcss.config.js postcss.config.cjs
```

**Missing sentence-transformers:**
If document processing fails with "Could not import sentence_transformers":
```bash
cd backend
pip install sentence-transformers
```

**Model decommissioned error:**
If you get "model has been decommissioned" error, ensure `.env` uses:
```env
MODEL_NAME=llama-3.3-70b-versatile
```
Then restart backend server (not just reload).

**CORS errors:**  
Verify `BACKEND_CORS_ORIGINS` in `.env` includes frontend URL

**Port conflicts:**  
Check if ports 5432 (PostgreSQL), 8000 (backend), 5173 (frontend) are available

## Production Deployment

1. Set strong `SECRET_KEY`
2. Configure production database
3. Update `BACKEND_CORS_ORIGINS`
4. Set appropriate `MAX_UPLOAD_SIZE`
5. Configure file storage (persistent volume)
6. Set up reverse proxy (nginx/caddy)
7. Enable HTTPS
8. Configure logging and monitoring

## License

This project is for educational and portfolio purposes.

## Acknowledgments

- FastAPI by Sebastián Ramírez
- Groq for fast LLM inference
- shadcn for UI components
