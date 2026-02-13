#!/bin/bash

# Stop API Server Script

PROJECT_DIR="/home/ubuntu/rohit/Funnel-Improvement-main"
PID_FILE="$PROJECT_DIR/api.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  API Server is not running (no PID file found)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "🛑 Stopping API Server (PID: $PID)..."
    kill "$PID"
    
    # Wait for process to stop
    sleep 2
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Process didn't stop gracefully, forcing..."
        kill -9 "$PID"
    fi
    
    rm "$PID_FILE"
    echo "✅ API Server stopped successfully"
else
    echo "⚠️  Process not running, cleaning up PID file"
    rm "$PID_FILE"
fi
