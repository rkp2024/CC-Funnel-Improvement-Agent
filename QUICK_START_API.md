# ⚡ Quick Start - API Integration
## Get Your Jupiter Edge+ Agent API Running in 5 Minutes

---

## 🚀 Option 1: Fastest Start (Direct)

```bash
cd /home/ubuntu/rohit/Funnel-Improvement-main

# 1. Install dependencies (if not already done)
source .venv/bin/activate
pip install fastapi uvicorn python-multipart

# 2. Start server
./start_api.sh

# 3. Test it
curl http://localhost:8000/health
```

**✅ Done! API is running at http://localhost:8000**

---

## 🐳 Option 2: Docker (Production Ready)

```bash
cd /home/ubuntu/rohit/Funnel-Improvement-main

# 1. Build and start
docker compose up -d

# 2. Check status
docker compose ps

# 3. Test it
curl http://localhost:8000/health
```

**✅ Done! Containerized API running**

---

## 🧪 Test Your API

### Quick Test
```bash
./test_api.sh
```

### Manual Test
```bash
# Chat with the bot
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: jupiter_api_key_2026" \
  -d '{
    "user_id": "919876543210",
    "message": "Hi, I want to apply for credit card",
    "user_name": "Rahul"
  }'
```

---

## 📱 WhatsApp Integration (3 Steps)

### 1. Expose Your API
```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Expose API
ngrok http 8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### 2. Configure WhatsApp
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create WhatsApp Business App
3. Go to WhatsApp → Configuration → Webhook
4. Enter webhook URL: `https://abc123.ngrok.io/webhook`
5. Enter verify token: `jupiter_edge_plus_2026`
6. Click "Verify and Save"
7. Subscribe to "messages" field

### 3. Test
Send a WhatsApp message to your test number!

---

## 📖 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: jupiter_api_key_2026" \
  -d '{"user_id": "test", "message": "Hi"}'
```

### API Docs
Open in browser: http://localhost:8000/docs

---

## 🔧 Management Commands

```bash
# Start API
./start_api.sh

# Stop API
./stop_api.sh

# Check status
./status_api.sh

# View logs
tail -f logs/api_server.log

# Run tests
./test_api.sh
```

---

## 🔐 Configuration

Edit `.env` file:
```env
API_KEY=your_secure_api_key
WHATSAPP_VERIFY_TOKEN=your_verify_token
HF_TOKEN=your_huggingface_token
```

---

## 📚 Full Documentation

- **API Testing:** `API_TESTING_GUIDE.md`
- **Docker Deployment:** `DOCKER_DEPLOYMENT.md`
- **WhatsApp Setup:** `WHATSAPP_INTEGRATION_README.md`
- **Complete Summary:** `API_INTEGRATION_SUMMARY.md`

---

## 🆘 Troubleshooting

### API won't start
```bash
# Check logs
cat logs/api_server.log

# Check if port is in use
lsof -i :8000

# Try different port
# Edit docker-compose.yml or start_api.sh
```

### Webhook verification fails
```bash
# Test webhook locally
curl "http://localhost:8000/webhook?mode=subscribe&challenge=test&verify_token=jupiter_edge_plus_2026"

# Should return: test
```

### Chat not working
```bash
# Check agent engine
curl http://localhost:8000/health

# Should show: "agent_initialized": true
```

---

## ✅ You're Ready!

Your API is now ready to:
- ✅ Receive chat messages
- ✅ Integrate with WhatsApp
- ✅ Handle multiple users
- ✅ Support Hindi/Hinglish
- ✅ Provide accurate answers with RAG

**Need help?** Check the full guides in the documentation files.

---

**Last Updated:** Feb 12, 2026
