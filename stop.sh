#!/bin/bash
# Stop script for Jupiter Edge+ AI Agent

cd /home/ubuntu/rohit/Funnel-Improvement-main

if [ -f app.pid ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🛑 Stopping application (PID: $PID)..."
        kill $PID
        sleep 2
        
        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Force stopping..."
            kill -9 $PID
        fi
        
        rm app.pid
        echo "✅ Application stopped"
    else
        echo "⚠️  Process $PID not running"
        rm app.pid
    fi
else
    echo "⚠️  No PID file found. Checking for running processes..."
    pkill -f "python app.py"
    echo "✅ Stopped any running instances"
fi
