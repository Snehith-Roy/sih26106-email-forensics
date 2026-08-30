.PHONY: setup dev-backend dev-frontend test train docker clean

# One-command setup
setup:
	bash setup.sh

# Start backend (dev mode with auto-reload)
dev-backend:
	cd backend && .venv/Scripts/activate && uvicorn app.main:app --reload --port 8000

# Start frontend (dev mode)
dev-frontend:
	cd frontend && npm run dev

# Run all backend tests
test:
	cd backend && .venv/Scripts/python.exe -m pytest tests/ -v --tb=short

# Retrain ML model
train:
	cd backend && .venv/Scripts/python.exe -m app.nlp.train_baseline

# Start with Docker
docker:
	docker-compose up --build

# Clean build artifacts
clean:
	rm -rf backend/__pycache__ backend/.pytest_cache
	rm -rf frontend/dist frontend/node_modules/.vite
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
