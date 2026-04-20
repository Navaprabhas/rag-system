.PHONY: help setup start stop restart logs clean test lint format

help:
	@echo "RAG System - Available Commands"
	@echo "================================"
	@echo "setup      - Initial setup (create .env, directories)"
	@echo "start      - Start all services with Docker Compose"
	@echo "stop       - Stop all services"
	@echo "restart    - Restart all services"
	@echo "logs       - View logs from all services"
	@echo "clean      - Remove containers, volumes, and cache"
	@echo "test       - Run test suite"
	@echo "lint       - Run code linting"
	@echo "format     - Format code with black"
	@echo "dev        - Start in development mode (local)"

setup:
	@echo "Setting up RAG System..."
	@cp -n .env.example .env || true
	@mkdir -p data logs data/cache
	@echo "✅ Setup complete. Edit .env with your API keys if needed."

start:
	@echo "Starting RAG System..."
	@docker-compose up -d
	@echo "✅ Services started"
	@echo "Frontend: http://localhost:8501"
	@echo "API: http://localhost:8000"

stop:
	@echo "Stopping RAG System..."
	@docker-compose down
	@echo "✅ Services stopped"

restart:
	@echo "Restarting RAG System..."
	@docker-compose restart
	@echo "✅ Services restarted"

logs:
	@docker-compose logs -f

clean:
	@echo "Cleaning up..."
	@docker-compose down -v
	@rm -rf data/cache/*
	@rm -rf logs/*
	@echo "✅ Cleanup complete"

test:
	@echo "Running tests..."
	@pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	@echo "Running linter..."
	@ruff check app/ tests/
	@mypy app/

format:
	@echo "Formatting code..."
	@black app/ tests/ frontend/
	@ruff check --fix app/ tests/

dev:
	@echo "Starting development mode..."
	@echo "Make sure Qdrant and Ollama are running separately"
	@uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
	@echo "✅ Dependencies installed"

build:
	@echo "Building Docker images..."
	@docker-compose build
	@echo "✅ Build complete"
