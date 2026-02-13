#!/bin/bash

# Start API Server Script for Jupiter Edge+ Credit Card Agent
# This script starts the FastAPI server in the background

PROJECT_DIR="/home/ubuntu/rohit/Funnel-Improvement-main"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/api.pid"
LOG_FILE="$LOG_DIR/api_server.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Check if API server is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  API Server is already running (PID: $PID)"
        echo "📍 Access API docs at: http://localhost:8000/docs"
        exit 1
    else
        echo "🧹 Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
if [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run: python3 -m venv .venv"
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "📦 Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the API server in the background
echo "🚀 Starting API Server..."
nohup python3 api_server.py > "$LOG_FILE" 2>&1 &

# Save the PID
echo $! > "$PID_FILE"

# Wait a moment for the server to start
sleep 3

# Check if the server started successfully
if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
    echo "✅ API Server started successfully!"
    echo "📝 PID: $(cat $PID_FILE)"
    echo "📋 Logs: $LOG_FILE"
    echo ""
    echo "📍 API Endpoints:"
    echo "   - Health Check: http://localhost:8000/health"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - Chat API: http://localhost:8000/api/chat"
    echo "   - WhatsApp Webhook: http://localhost:8000/webhook"
    echo ""
    echo "🔍 View logs: tail -f $LOG_FILE"
    echo "🛑 Stop server: ./stop_api.sh"
else
    echo "❌ Failed to start API Server"
    echo "📋 Check logs: cat $LOG_FILE"
    rm "$PID_FILE"
    exit 1
fi
