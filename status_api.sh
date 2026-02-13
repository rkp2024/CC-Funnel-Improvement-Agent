#!/bin/bash

# Check API Server Status

PROJECT_DIR="/home/ubuntu/rohit/Funnel-Improvement-main"
PID_FILE="$PROJECT_DIR/api.pid"
LOG_FILE="$PROJECT_DIR/logs/api_server.log"

echo "🔍 Jupiter Edge+ API Server Status"
echo "=================================="

if [ ! -f "$PID_FILE" ]; then
    echo "❌ API Server is NOT running (no PID file)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ API Server is RUNNING"
    echo "📝 PID: $PID"
    echo "📋 Log file: $LOG_FILE"
    echo ""
    echo "📍 Endpoints:"
    echo "   - http://localhost:8000/health"
    echo "   - http://localhost:8000/docs"
    echo "   - http://localhost:8000/api/chat"
    echo ""
    echo "💾 Memory usage:"
    ps -p "$PID" -o pid,vsz,rss,comm
    echo ""
    echo "📊 Recent logs (last 10 lines):"
    echo "---"
    tail -n 10 "$LOG_FILE" 2>/dev/null || echo "No logs available"
else
    echo "❌ API Server is NOT running (stale PID file)"
    rm "$PID_FILE"
    exit 1
fi
