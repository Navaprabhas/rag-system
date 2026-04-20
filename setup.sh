#!/bin/bash

# RAG System Setup Script

set -e

echo "🚀 Setting up RAG System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your API keys if needed."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs data/cache

# Pull and start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check Qdrant health
echo "🔍 Checking Qdrant..."
until curl -f http://localhost:6333/health &> /dev/null; do
    echo "Waiting for Qdrant..."
    sleep 2
done
echo "✅ Qdrant is ready"

# Check FastAPI health
echo "🔍 Checking FastAPI..."
until curl -f http://localhost:8000/api/v1/health &> /dev/null; do
    echo "Waiting for FastAPI..."
    sleep 2
done
echo "✅ FastAPI is ready"

echo ""
echo "🎉 RAG System is ready!"
echo ""
echo "📍 Access points:"
echo "   - Frontend:  http://localhost:8501"
echo "   - API:       http://localhost:8000"
echo "   - API Docs:  http://localhost:8000/docs"
echo "   - Qdrant:    http://localhost:6333/dashboard"
echo ""
echo "📚 Next steps:"
echo "   1. Open http://localhost:8501 in your browser"
echo "   2. Upload documents or paste URLs"
echo "   3. Start asking questions!"
echo ""
echo "🛠️  Useful commands:"
echo "   - View logs:     docker-compose logs -f"
echo "   - Stop system:   docker-compose down"
echo "   - Restart:       docker-compose restart"
echo ""
