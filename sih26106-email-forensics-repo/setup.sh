#!/usr/bin/env bash
# SIH26106 — One-command dev environment setup
# Usage: bash setup.sh
set -euo pipefail

echo "============================================="
echo "  SIH26106 Email Forensics — Setup"
echo "============================================="

# ── 1. Python backend ──────────────────────────────────────────────
echo ""
echo "[1/5] Setting up Python backend..."
cd backend

if [ ! -d ".venv" ]; then
    python3 -m venv .venv 2>/dev/null || python -m venv .venv
fi

# Activate (works on both Unix and Git Bash on Windows)
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

pip install -q -r requirements.txt
echo "  ✓ Backend dependencies installed"

# ── 2. Train ML model ─────────────────────────────────────────────
echo ""
echo "[2/5] Training NLP classifier (TF-IDF + XGBoost)..."
python -m app.nlp.prepare_dataset 2>/dev/null || true
python -m app.nlp.train_baseline 2>/dev/null || echo "  ⚠ XGBoost training skipped (mock fallback active)"

# ── 3. Database init ───────────────────────────────────────────────
echo ""
echo "[3/5] Initializing database..."
python -c "from app.db import init_db; init_db()" 2>/dev/null || echo "  ⚠ DB init skipped (will auto-create on first request)"

cd ..

# ── 4. Frontend ────────────────────────────────────────────────────
echo ""
echo "[4/5] Setting up frontend..."
cd frontend

if command -v npm &> /dev/null; then
    npm install --silent 2>/dev/null
    echo "  ✓ Frontend dependencies installed"
else
    echo "  ⚠ npm not found — skipping frontend setup"
fi

cd ..

# ── 5. Environment file ────────────────────────────────────────────
echo ""
echo "[5/5] Checking environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ✓ Created .env from .env.example — add your API keys"
else
    echo "  ✓ .env already exists"
fi

echo ""
echo "============================================="
echo "  Setup complete!"
echo "============================================="
echo ""
echo "To start the backend:"
echo "  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "To start the frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "To start with Docker (requires Docker Desktop):"
echo "  docker-compose up --build"
echo ""
echo "API docs: http://localhost:8000/docs"
echo "Dashboard: http://localhost:5173"
echo ""
