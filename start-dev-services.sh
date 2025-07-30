#!/bin/bash
# Start development services for GENESIS

echo "🚀 Starting GENESIS Development Services..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Load environment variables if .env exists
if [ -f backend/.env ]; then
    echo "📋 Loading environment variables from backend/.env"
    export $(cat backend/.env | grep -v '^#' | xargs)
fi

# Start Redis only (minimal setup)
echo "🔄 Starting Redis..."
docker-compose -f docker-compose.dev.yml up -d redis

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
for i in {1..30}; do
    if docker-compose -f docker-compose.dev.yml exec redis redis-cli ping &> /dev/null; then
        echo "✅ Redis is ready!"
        break
    fi
    sleep 1
done

# Show status
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "🔗 Service URLs:"
echo "   - Redis: redis://localhost:6379"
echo ""
echo "💡 To start all services (including monitoring):"
echo "   docker-compose -f docker-compose.dev.yml up -d"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f docker-compose.dev.yml down"