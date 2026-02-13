# 🚀 API Testing Guide
## Jupiter Edge+ Credit Card Agent - WhatsApp Integration API

---

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [API Endpoints](#api-endpoints)
3. [Testing with cURL](#testing-with-curl)
4. [Testing with Postman](#testing-with-postman)
5. [WhatsApp Integration](#whatsapp-integration)
6. [Authentication](#authentication)
7. [Error Handling](#error-handling)
8. [Production Deployment](#production-deployment)

---

## 🎯 Quick Start

### 1. Install Dependencies

```bash
cd /home/ubuntu/rohit/Funnel-Improvement-main

# Activate virtual environment
source .venv/bin/activate

# Install new dependencies
pip install fastapi uvicorn python-multipart
```

### 2. Configure Environment

Create a `.env` file (copy from `env.example`):

```bash
cp env.example .env
nano .env
```

Update the following:
```env
# API Configuration
API_KEY=your_secure_api_key_here

# WhatsApp Configuration
WHATSAPP_VERIFY_TOKEN=your_verify_token_here
WHATSAPP_APP_SECRET=your_app_secret_here

# Hugging Face (already configured)
HF_TOKEN=your_existing_token
```

### 3. Start API Server

```bash
# Make scripts executable
chmod +x start_api.sh stop_api.sh status_api.sh

# Start the API server
./start_api.sh
```

**Expected Output:**
```
✅ API Server started successfully!
📝 PID: 12345
📋 Logs: logs/api_server.log

📍 API Endpoints:
   - Health Check: http://localhost:8000/health
   - API Docs: http://localhost:8000/docs
   - Chat API: http://localhost:8000/api/chat
   - WhatsApp Webhook: http://localhost:8000/webhook
```

### 4. Verify Server is Running

```bash
# Check status
./status_api.sh

# Or test health endpoint
curl http://localhost:8000/health
```

---

## 📡 API Endpoints

### Base URL
- **Local:** `http://localhost:8000`
- **Production:** `https://your-domain.com`

### Endpoints Overview

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/` | Root endpoint | No |
| GET | `/health` | Health check | No |
| GET | `/docs` | Interactive API docs | No |
| POST | `/api/chat` | Send message to agent | Yes (API Key) |
| POST | `/api/reset` | Reset user session | Yes (API Key) |
| GET | `/api/session/{user_id}` | Get session info | Yes (API Key) |
| GET | `/api/stats` | Get API statistics | Yes (API Key) |
| GET | `/webhook` | WhatsApp verification | No |
| POST | `/webhook` | WhatsApp messages | Yes (Signature) |

---

## 🧪 Testing with cURL

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-12T10:30:00.123456",
  "agent_initialized": true,
  "version": "1.0.0"
}
```

### 2. Chat API - Send Message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: jupiter_api_key_2026" \
  -d '{
    "user_id": "919876543210",
    "message": "Hi, I want to apply for credit card",
    "user_name": "Rahul"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "user_id": "919876543210",
  "message": "Hi Rahul! 👋 I'm here to help you with your Jupiter Edge+ Credit Card application...",
  "intent": "GREETING",
  "language": "ENGLISH",
  "timestamp": "2026-02-12T10:30:00.123456",
  "session_id": "919876543210"
}
```

### 3. Test Hindi/Hinglish Message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: jupiter_api_key_2026" \
  -d '{
    "user_id": "919876543210",
    "message": "Namaste, mujhe credit card chahiye"
  }'
```

### 4. Test Product Query

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: jupiter_api_key_2026" \
  -d '{
    "user_id": "919876543210",
    "message": "What is the cashback on shopping?"
  }'
```

### 5. Test Off-Topic Question

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: jupiter_api_key_2026" \
  -d '{
    "user_id": "919876543210",
    "message": "Who is Narendra Modi?"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "user_id": "919876543210",
  "message": "I can only help with Jupiter Edge+ card. Is there anything about the card I can help you with?",
  "intent": "OFF_TOPIC",
  "language": "ENGLISH",
  "timestamp": "2026-02-12T10:30:00.123456"
}
```

### 6. Get Session Information

```bash
curl http://localhost:8000/api/session/919876543210 \
  -H "X-API-Key: jupiter_api_key_2026"
```

### 7. Reset User Session

```bash
curl -X POST http://localhost:8000/api/reset \
  -H "Content-Type: application/json" \
  -H "X-API-Key: jupiter_api_key_2026" \
  -d '{
    "user_id": "919876543210"
  }'
```

### 8. Get API Statistics

```bash
curl http://localhost:8000/api/stats \
  -H "X-API-Key: jupiter_api_key_2026"
```

---

## 📮 Testing with Postman

### 1. Import Collection

Create a new Postman collection with the following requests:

#### Environment Variables
```
base_url = http://localhost:8000
api_key = jupiter_api_key_2026
user_id = 919876543210
```

#### Request 1: Health Check
- **Method:** GET
- **URL:** `{{base_url}}/health`
- **Headers:** None

#### Request 2: Chat - Greeting
- **Method:** POST
- **URL:** `{{base_url}}/api/chat`
- **Headers:**
  - `Content-Type: application/json`
  - `X-API-Key: {{api_key}}`
- **Body (JSON):**
```json
{
  "user_id": "{{user_id}}",
  "message": "Hi, I want to apply for credit card",
  "user_name": "Rahul"
}
```

#### Request 3: Chat - Product Query
- **Method:** POST
- **URL:** `{{base_url}}/api/chat`
- **Headers:**
  - `Content-Type: application/json`
  - `X-API-Key: {{api_key}}`
- **Body (JSON):**
```json
{
  "user_id": "{{user_id}}",
  "message": "What are the fees?"
}
```

#### Request 4: Chat - Hinglish
- **Method:** POST
- **URL:** `{{base_url}}/api/chat`
- **Headers:**
  - `Content-Type: application/json`
  - `X-API-Key: {{api_key}}`
- **Body (JSON):**
```json
{
  "user_id": "{{user_id}}",
  "message": "Physical PAN card nahi hai"
}
```

#### Request 5: Reset Session
- **Method:** POST
- **URL:** `{{base_url}}/api/reset`
- **Headers:**
  - `Content-Type: application/json`
  - `X-API-Key: {{api_key}}`
- **Body (JSON):**
```json
{
  "user_id": "{{user_id}}"
}
```

### 2. Test Scenarios

**Scenario 1: New User Onboarding**
1. Reset session
2. Send greeting: "Hi"
3. Ask about card: "Tell me about the card"
4. Ask about eligibility: "Am I eligible?"
5. Ask about documents: "What documents do I need?"

**Scenario 2: Hindi User**
1. Reset session
2. Send: "Namaste"
3. Send: "Credit card ke baare mein batao"
4. Send: "Cashback kitna milega?"

**Scenario 3: Edge Cases**
1. Off-topic: "Who is the Prime Minister?"
2. Unsupported language: "¿Cómo estás?" (Spanish)
3. Empty message: ""
4. Very long message (500+ words)

---

## 📱 WhatsApp Integration

### Setup WhatsApp Business API

#### 1. Create WhatsApp Business App
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app
3. Add WhatsApp product
4. Get your credentials:
   - Phone Number ID
   - Access Token
   - App Secret

#### 2. Configure Webhook

**Webhook URL:** `https://your-domain.com/webhook`

**Verification:**
- The GET endpoint will be called by WhatsApp
- Must return the `challenge` parameter
- Verify token must match your configured token

**Test Webhook Verification:**
```bash
curl "http://localhost:8000/webhook?mode=subscribe&challenge=test123&verify_token=jupiter_edge_plus_2026"
```

Expected: Returns `test123`

#### 3. WhatsApp Webhook Payload Format

When a user sends a message, WhatsApp will POST to `/webhook`:

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "15551234567",
          "phone_number_id": "PHONE_NUMBER_ID"
        },
        "contacts": [{
          "profile": {
            "name": "Rahul Kumar"
          },
          "wa_id": "919876543210"
        }],
        "messages": [{
          "from": "919876543210",
          "id": "wamid.XXX",
          "timestamp": "1234567890",
          "text": {
            "body": "Hi, I want to apply for credit card"
          },
          "type": "text"
        }]
      },
      "field": "messages"
    }]
  }]
}
```

#### 4. Test Webhook with Sample Payload

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "changes": [{
        "value": {
          "contacts": [{
            "profile": {"name": "Rahul"},
            "wa_id": "919876543210"
          }],
          "messages": [{
            "from": "919876543210",
            "id": "msg123",
            "timestamp": "1234567890",
            "text": {"body": "Hi, I want credit card"},
            "type": "text"
          }]
        }
      }]
    }]
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "response": "Hi Rahul! 👋 I'm here to help...",
  "whatsapp_payload": {
    "messaging_product": "whatsapp",
    "to": "919876543210",
    "type": "text",
    "text": {
      "body": "Hi Rahul! 👋 I'm here to help..."
    }
  }
}
```

---

## 🔐 Authentication

### API Key Authentication

All `/api/*` endpoints require an API key in the header:

```
X-API-Key: your_api_key_here
```

**Configure API Key:**
1. Set in `.env` file: `API_KEY=your_secure_key`
2. Or set environment variable: `export API_KEY=your_secure_key`

**Test without API Key:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "hi"}'
```

Expected: `401 Unauthorized`

### WhatsApp Webhook Security

WhatsApp signs webhook requests with HMAC SHA256.

**Configure:**
```env
WHATSAPP_APP_SECRET=your_app_secret
```

The API automatically verifies the `X-Hub-Signature-256` header.

---

## ⚠️ Error Handling

### Common Errors

#### 1. 401 Unauthorized
```json
{
  "error": true,
  "detail": "Invalid API key",
  "timestamp": "2026-02-12T10:30:00"
}
```
**Fix:** Add correct `X-API-Key` header

#### 2. 503 Service Unavailable
```json
{
  "error": true,
  "detail": "Service temporarily unavailable",
  "timestamp": "2026-02-12T10:30:00"
}
```
**Fix:** Agent engine not initialized. Check logs and restart.

#### 3. 404 Not Found
```json
{
  "error": true,
  "detail": "Session not found",
  "timestamp": "2026-02-12T10:30:00"
}
```
**Fix:** User has no active session. Send a message first.

#### 4. 400 Bad Request
```json
{
  "error": true,
  "detail": "Invalid JSON",
  "timestamp": "2026-02-12T10:30:00"
}
```
**Fix:** Check JSON syntax in request body

---

## 🌐 Production Deployment

### 1. Expose API to Internet

#### Option A: ngrok (Quick Testing)
```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Authenticate
ngrok authtoken YOUR_AUTH_TOKEN

# Expose API
ngrok http 8000
```

Your webhook URL: `https://xyz123.ngrok.io/webhook`

#### Option B: Reverse Proxy (Production)

**Install Nginx:**
```bash
sudo apt update
sudo apt install nginx
```

**Configure Nginx:**
```nginx
# /etc/nginx/sites-available/jupiter-api
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/jupiter-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Add SSL (Let's Encrypt):**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. Configure WhatsApp Webhook

1. Go to WhatsApp Business Dashboard
2. Navigate to Configuration → Webhook
3. Enter webhook URL: `https://your-domain.com/webhook`
4. Enter verify token: (from your `.env`)
5. Click "Verify and Save"
6. Subscribe to `messages` webhook field

### 3. Production Environment Variables

```env
# Production settings
ENVIRONMENT=production
API_KEY=STRONG_RANDOM_KEY_HERE
WHATSAPP_APP_SECRET=YOUR_ACTUAL_SECRET
WHATSAPP_VERIFY_TOKEN=YOUR_ACTUAL_TOKEN
```

### 4. Monitor Logs

```bash
# API server logs
tail -f logs/api_server.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📊 Testing Checklist

### Basic Functionality
- [ ] Health check returns 200
- [ ] API docs accessible at `/docs`
- [ ] Chat endpoint accepts messages
- [ ] Responses are in correct format
- [ ] API key authentication works

### Language Detection
- [ ] English messages detected correctly
- [ ] Hindi (Devanagari) messages detected
- [ ] Hinglish messages detected
- [ ] Unsupported languages handled

### Intent Classification
- [ ] Greetings recognized
- [ ] Off-topic questions redirected
- [ ] Product queries answered
- [ ] Document questions answered (PAN/Aadhaar)

### RAG Integration
- [ ] Cashback queries return specific numbers
- [ ] Fee queries return accurate information
- [ ] Eligibility queries answered
- [ ] Application process explained

### Session Management
- [ ] Sessions persist across messages
- [ ] Session info retrievable
- [ ] Sessions can be reset
- [ ] Multiple users handled independently

### WhatsApp Integration
- [ ] Webhook verification works
- [ ] Webhook accepts messages
- [ ] Messages extracted correctly
- [ ] Responses formatted for WhatsApp

### Error Handling
- [ ] Invalid API key returns 401
- [ ] Missing fields return 400
- [ ] Service errors return 503
- [ ] All errors have proper format

### Performance
- [ ] Response time < 3 seconds
- [ ] Handles concurrent requests
- [ ] No memory leaks
- [ ] Logs don't fill disk

---

## 🔧 Troubleshooting

### API Server Won't Start

**Check logs:**
```bash
cat logs/api_server.log
```

**Common issues:**
- Port 8000 already in use: Change `API_PORT` in `.env`
- Agent engine initialization failed: Check RAG data files
- Missing dependencies: Run `pip install -r requirements.txt`

### Webhook Not Receiving Messages

**Verify webhook:**
```bash
curl "https://your-domain.com/webhook?mode=subscribe&challenge=test&verify_token=YOUR_TOKEN"
```

**Check:**
- Webhook URL is publicly accessible
- SSL certificate is valid
- Verify token matches WhatsApp configuration
- Webhook subscribed to `messages` field

### API Responses Are Slow

**Check:**
- Hugging Face API rate limits
- Network latency to HF servers
- RAG engine performance
- Server resources (CPU/RAM)

**Optimize:**
- Use faster model (Mistral 7B is already fast)
- Reduce `max_new_tokens` in API call
- Cache frequent queries
- Use Redis for session storage

---

## 📞 Support

For issues or questions:
- Check logs: `tail -f logs/api_server.log`
- View API docs: `http://localhost:8000/docs`
- Test health: `curl http://localhost:8000/health`

---

**Last Updated:** Feb 12, 2026  
**Version:** 1.0.0
