# Quick Start Guide

## Setup in 5 Minutes

### Step 1: Get Groq API Key (1 min)

1. Visit https://console.groq.com
2. Sign up (free account)
3. Go to API Keys → Create API Key
4. Copy your key (starts with `gsk_...`)

### Step 2: Start Database (30 seconds)

```bash
docker-compose up -d
```

### Step 3: Backend Setup (2 min)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Copy and edit .env file
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

Edit `backend/.env`:
- Replace `GROQ_API_KEY` with your actual key
- Set `SECRET_KEY` to a random string

### Step 4: Frontend Setup (1 min)

```bash
cd frontend
npm install
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

### Step 5: Run Application (30 seconds)

**Terminal 1 (Backend):**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### Step 6: Open Browser

Visit http://localhost:5173 and start chatting with your documents.

## Testing

**Backend:**
```bash
cd backend
pytest --cov=app
```

**Frontend:**
```bash
cd frontend
npm test
```

## Common Issues

**Environment variable changes not applied:**
After editing `.env` files, stop backend (Ctrl+C) and restart. Auto-reload doesn't detect .env changes.

**PostCSS error on frontend:**
```bash
cd frontend
mv postcss.config.js postcss.config.cjs
```

**sentence-transformers missing:**
```bash
cd backend
pip install sentence-transformers
```

**Model decommissioned error:**
Ensure `backend/.env` has `MODEL_NAME=llama-3.3-70b-versatile`, then restart backend.

**Port in use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

**Database not starting:**
```bash
docker-compose down
docker-compose up -d
docker-compose logs postgres
```

**Module not found:**
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

## What You Built

- Full-stack RAG application
- Document upload and processing
- AI-powered chat interface
- Dark/light mode
- 80%+ test coverage
- CI/CD with GitHub Actions
- Production-ready code
- SOLID principles
- Clean architecture
