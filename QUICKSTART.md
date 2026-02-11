# Quick Start Guide

### Step 1: Get Groq API Key

1. Sign up at https://console.groq.com
2. Create an API key
3. Copy your key (starts with `gsk_...`)

### Step 2: Start Database

```bash
docker-compose up -d
```

### Step 3: Backend Setup

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

### Step 4: Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

### Step 5: Run Application

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

## Common Issues

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

**Database not starting:**
```bash
docker-compose restart postgres
docker-compose logs postgres
```
