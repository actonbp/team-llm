#!/bin/bash

# Team-LLM Platform Quick Start Script

echo "🚀 Starting Team-LLM Platform..."

# Check if .env file exists
if [ ! -f backend/.env ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env with your API keys before continuing."
    echo "   Press Enter when ready..."
    read
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data uploads config

# Start the services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Team-LLM Platform is running!"
    echo ""
    echo "🌐 Access the platform at:"
    echo "   - Participant Interface: http://localhost:8080"
    echo "   - API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📖 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi