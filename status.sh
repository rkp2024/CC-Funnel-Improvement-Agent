#!/bin/bash
# Status script for Jupiter Edge+ AI Agent

cd /home/ubuntu/rohit/Funnel-Improvement-main

echo "📊 Jupiter Edge+ AI Agent Status"
echo "================================"
echo ""

if [ -f app.pid ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Status: RUNNING"
        echo "🔢 PID: $PID"
        echo "⏱️  Uptime: $(ps -p $PID -o etime= | xargs)"
        echo "💾 Memory: $(ps -p $PID -o rss= | awk '{printf "%.1f MB", $1/1024}')"
        echo "🌐 Port: 8080"
        echo ""
        echo "📝 Recent logs (last 10 lines):"
        echo "---"
        tail -10 logs/app.log 2>/dev/null || echo "No logs available"
    else
        echo "❌ Status: NOT RUNNING (stale PID file)"
        rm app.pid
    fi
else
    # Check if process is running without PID file
    if pgrep -f "python app.py" > /dev/null; then
        echo "⚠️  Status: RUNNING (no PID file)"
        echo "🔢 PIDs: $(pgrep -f 'python app.py' | xargs)"
        echo ""
        echo "Run ./stop.sh to stop the process"
    else
        echo "❌ Status: NOT RUNNING"
        echo ""
        echo "Run ./start.sh to start the application"
    fi
fi
