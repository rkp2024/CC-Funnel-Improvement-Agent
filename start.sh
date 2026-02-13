#!/bin/bash
# Start script for Jupiter Edge+ AI Agent

cd /home/ubuntu/rohit/Funnel-Improvement-main

# Activate virtual environment and run in background with nohup
source .venv/bin/activate

# Start the application in background
nohup python app.py > logs/app.log 2>&1 &

# Save the PID
echo $! > app.pid

echo "✅ Application started in background (PID: $(cat app.pid))"
echo "📝 Logs: logs/app.log"
echo "🌐 Access at: http://localhost:8080"
echo ""
echo "To stop: ./stop.sh"
echo "To check status: ./status.sh"
