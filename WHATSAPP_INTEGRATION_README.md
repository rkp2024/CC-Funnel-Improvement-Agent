# 📱 WhatsApp Integration Guide
## Jupiter Edge+ Credit Card Agent - Complete Setup

---

## 🎯 Overview

This guide walks you through integrating the Jupiter Edge+ Credit Card Agent with WhatsApp Business API. After completion, users will be able to chat with the AI agent directly through WhatsApp.

**What you'll build:**
- WhatsApp Business API webhook integration
- Bi-directional messaging (receive & send)
- Secure message handling with signature verification
- Production-ready deployment

---

## 📋 Prerequisites

### 1. WhatsApp Business Account
- Meta Business Account
- WhatsApp Business App (created in Meta for Developers)
- Phone number for WhatsApp Business

### 2. Server Requirements
- Public domain or IP address
- SSL certificate (HTTPS required)
- Port 443 accessible
- API server running (see deployment guide)

### 3. Technical Requirements
- API server deployed and accessible
- Environment variables configured
- Webhook endpoint ready

---

## 🚀 Step-by-Step Setup

### Step 1: Create WhatsApp Business App

1. **Go to Meta for Developers**
   - Visit: https://developers.facebook.com/
   - Log in with your Facebook account

2. **Create New App**
   - Click "Create App"
   - Select "Business" as app type
   - Fill in app details:
     - App Name: "Jupiter Edge+ Credit Card Agent"
     - Contact Email: your-email@example.com
     - Business Account: Select your business

3. **Add WhatsApp Product**
   - In app dashboard, click "Add Product"
   - Find "WhatsApp" and click "Set Up"

### Step 2: Get API Credentials

1. **Phone Number ID**
   - Go to WhatsApp → Getting Started
   - Copy the "Phone number ID"
   - Save it: `WHATSAPP_PHONE_NUMBER_ID=123456789`

2. **Access Token**
   - In the same page, copy the "Temporary access token"
   - For production, generate a permanent token:
     - Go to Settings → Basic
     - Generate System User Token
   - Save it: `WHATSAPP_ACCESS_TOKEN=EAAxxxxx...`

3. **App Secret**
   - Go to Settings → Basic
   - Click "Show" next to App Secret
   - Save it: `WHATSAPP_APP_SECRET=abc123...`

4. **Verify Token (Create Your Own)**
   - Create a random string (e.g., `jupiter_edge_plus_2026`)
   - Save it: `WHATSAPP_VERIFY_TOKEN=jupiter_edge_plus_2026`

### Step 3: Configure Environment

Update your `.env` file:

```env
# WhatsApp Configuration
WHATSAPP_VERIFY_TOKEN=jupiter_edge_plus_2026
WHATSAPP_APP_SECRET=your_app_secret_from_meta
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token_from_meta

# API Configuration
API_KEY=your_secure_api_key
HF_TOKEN=your_huggingface_token
```

### Step 4: Deploy API Server

#### Option A: Using Docker (Recommended)

```bash
cd /home/ubuntu/rohit/Funnel-Improvement-main

# Build and start
docker compose up -d

# Verify
curl http://localhost:8000/health
```

#### Option B: Direct Deployment

```bash
cd /home/ubuntu/rohit/Funnel-Improvement-main

# Start API server
./start_api.sh

# Verify
./status_api.sh
```

### Step 5: Expose API to Internet

#### Option A: Using ngrok (Quick Testing)

```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Authenticate (get token from ngrok.com)
ngrok authtoken YOUR_NGROK_TOKEN

# Expose API
ngrok http 8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

#### Option B: Using Domain with Nginx (Production)

See `API_TESTING_GUIDE.md` for detailed Nginx setup.

**Your webhook URL will be:**
```
https://your-domain.com/webhook
```

### Step 6: Configure WhatsApp Webhook

1. **Go to WhatsApp Configuration**
   - In Meta for Developers dashboard
   - Go to WhatsApp → Configuration

2. **Set Webhook URL**
   - Click "Edit" next to Webhook
   - Enter your webhook URL:
     - ngrok: `https://abc123.ngrok.io/webhook`
     - Domain: `https://your-domain.com/webhook`
   - Enter Verify Token: `jupiter_edge_plus_2026` (from your .env)
   - Click "Verify and Save"

3. **Subscribe to Webhook Fields**
   - Check "messages" field
   - Click "Subscribe"

**Expected Result:** ✅ Webhook verified successfully

### Step 7: Test Webhook

#### Test Verification Endpoint

```bash
curl "https://your-domain.com/webhook?mode=subscribe&challenge=test123&verify_token=jupiter_edge_plus_2026"
```

**Expected:** Returns `test123`

#### Test Message Webhook

```bash
curl -X POST https://your-domain.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "changes": [{
        "value": {
          "contacts": [{"profile": {"name": "Test User"}, "wa_id": "919876543210"}],
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

**Expected:** JSON response with bot's reply

### Step 8: Send Messages Back to WhatsApp

The API currently logs responses. To actually send messages to WhatsApp, you need to call WhatsApp's Send Message API.

#### Install WhatsApp Client (Optional)

```bash
pip install requests
```

#### Create Send Message Function

Create `whatsapp_client.py`:

```python
import requests
import os

WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

def send_whatsapp_message(to: str, message: str):
    """Send message to WhatsApp user"""
    url = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

#### Update `api_server.py`

Add this import at the top:
```python
from whatsapp_client import send_whatsapp_message
```

In the `/webhook` POST handler, after getting the response, add:
```python
# Send response back to WhatsApp
send_whatsapp_message(user_id, response_text)
```

### Step 9: Test End-to-End

1. **Add Test Number**
   - Go to WhatsApp → API Setup
   - Add your phone number to "To" field
   - Verify with OTP

2. **Send Test Message**
   - Open WhatsApp on your phone
   - Send message to the test number
   - Example: "Hi, I want to apply for credit card"

3. **Verify Response**
   - Check API logs: `tail -f logs/api_server.log`
   - You should see:
     - Incoming message received
     - Agent processing
     - Response generated
     - Message sent back

4. **Check WhatsApp**
   - You should receive the bot's response in WhatsApp

---

## 🔒 Security Best Practices

### 1. Signature Verification

The API automatically verifies WhatsApp's signature:

```python
# In api_server.py - already implemented
if WHATSAPP_APP_SECRET and x_hub_signature_256:
    if not verify_webhook_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
```

### 2. Use Environment Variables

Never hardcode credentials:

```bash
# ❌ BAD
WHATSAPP_ACCESS_TOKEN = "EAAxxxxx"

# ✅ GOOD
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
```

### 3. HTTPS Only

WhatsApp requires HTTPS for webhooks. Use:
- Let's Encrypt for free SSL
- Cloudflare for SSL proxy
- AWS Certificate Manager

### 4. Rate Limiting

Implement rate limiting to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/webhook")
@limiter.limit("100/minute")
async def handle_webhook(...):
    ...
```

### 5. IP Whitelisting

Restrict webhook to Meta's IPs (optional):

```python
META_IPS = [
    "157.240.0.0/16",
    "31.13.24.0/21",
    # Add more from Meta's documentation
]

def is_meta_ip(ip: str) -> bool:
    # Check if IP is in allowed ranges
    ...
```

---

## 📊 Monitoring & Debugging

### View Logs

```bash
# API server logs
tail -f logs/api_server.log

# Filter for webhook events
grep "webhook" logs/api_server.log

# Filter for errors
grep "ERROR" logs/api_server.log
```

### Check Webhook Status

1. Go to Meta for Developers
2. WhatsApp → Configuration → Webhooks
3. View recent webhook calls and responses

### Test Webhook Locally

Use the test script:

```bash
./test_api.sh
```

### Common Issues

#### Issue 1: Webhook Verification Failed

**Symptoms:** "Verification failed" in Meta dashboard

**Solutions:**
- Check verify token matches in `.env` and Meta dashboard
- Ensure webhook URL is accessible (test with curl)
- Check API server logs for errors

#### Issue 2: Messages Not Received

**Symptoms:** No webhook calls in logs

**Solutions:**
- Verify webhook subscribed to "messages" field
- Check phone number is added to test numbers
- Ensure API server is running: `./status_api.sh`
- Test webhook manually with curl

#### Issue 3: Signature Verification Failed

**Symptoms:** 401 errors in logs

**Solutions:**
- Verify `WHATSAPP_APP_SECRET` is correct
- Check signature header: `X-Hub-Signature-256`
- Temporarily disable verification for testing (not recommended for production)

#### Issue 4: Messages Not Sent Back

**Symptoms:** Bot processes but user doesn't receive reply

**Solutions:**
- Check `WHATSAPP_ACCESS_TOKEN` is valid
- Verify `WHATSAPP_PHONE_NUMBER_ID` is correct
- Check WhatsApp API rate limits
- Review WhatsApp API response in logs

---

## 🧪 Testing Scenarios

### Test 1: Basic Greeting

**User sends:** "Hi"

**Expected:**
- Language: ENGLISH
- Intent: GREETING
- Response: Welcome message with user's name

### Test 2: Hindi Message

**User sends:** "Namaste"

**Expected:**
- Language: HINDI or HINGLISH
- Intent: GREETING
- Response: Hindi/Hinglish greeting

### Test 3: Product Query

**User sends:** "What is the cashback?"

**Expected:**
- Intent: ASKING_ABOUT_CASHBACK
- Response: Specific cashback percentages (10%, 5%, 7%, 1%)

### Test 4: Document Question

**User sends:** "Do I need physical PAN card?"

**Expected:**
- Intent: ASKING_ABOUT_PAN
- Response: Clarification about PAN number vs physical card

### Test 5: Off-Topic Question

**User sends:** "Who is the Prime Minister?"

**Expected:**
- Intent: OFF_TOPIC
- Response: Polite redirect to card topics

### Test 6: Application Flow

**User sends:**
1. "Hi"
2. "Tell me about the card"
3. "What documents do I need?"
4. "How do I apply?"

**Expected:** Conversational flow with context maintained

---

## 🌐 Production Deployment Checklist

### Pre-Launch

- [ ] API server running and stable
- [ ] Environment variables configured
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Webhook verified in Meta dashboard
- [ ] Signature verification enabled
- [ ] Test messages working end-to-end
- [ ] Logs configured and monitored
- [ ] Error handling tested
- [ ] Rate limiting implemented
- [ ] Backup and recovery plan ready

### Launch

- [ ] Move from test phone numbers to production
- [ ] Generate permanent access token
- [ ] Update webhook URL to production domain
- [ ] Enable monitoring and alerts
- [ ] Document incident response procedures

### Post-Launch

- [ ] Monitor webhook success rate
- [ ] Track response times
- [ ] Review user conversations
- [ ] Collect feedback
- [ ] Iterate on responses

---

## 📈 Scaling Considerations

### High Volume

For > 1000 messages/day:

1. **Use Message Queue**
   - Redis + Celery for async processing
   - RabbitMQ for message buffering

2. **Load Balancing**
   - Multiple API instances
   - Nginx load balancer

3. **Caching**
   - Redis for session storage
   - Cache frequent queries

4. **Database**
   - PostgreSQL for conversation history
   - MongoDB for analytics

### Example Architecture

```
WhatsApp → Webhook → Load Balancer → API Instances
                                    ↓
                              Redis Cache
                                    ↓
                            Message Queue (Celery)
                                    ↓
                            Agent Workers (3+)
                                    ↓
                            PostgreSQL DB
```

---

## 🔧 Advanced Configuration

### Custom Message Templates

WhatsApp supports rich message templates:

```python
def send_template_message(to: str, template_name: str, params: list):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in params]
                }
            ]
        }
    }
    # Send to WhatsApp API
```

### Interactive Buttons

```python
def send_button_message(to: str, text: str, buttons: list):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                    for b in buttons
                ]
            }
        }
    }
    # Send to WhatsApp API
```

### Media Messages

```python
def send_image_message(to: str, image_url: str, caption: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }
    # Send to WhatsApp API
```

---

## 📞 Support & Resources

### Official Documentation
- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp)
- [Meta for Developers](https://developers.facebook.com/)
- [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)

### Useful Tools
- [Postman Collection for WhatsApp API](https://www.postman.com/meta/workspace/whatsapp-business-platform)
- [WhatsApp API Explorer](https://developers.facebook.com/tools/explorer/)

### Troubleshooting
- Check API server logs: `tail -f logs/api_server.log`
- Test webhook: `./test_api.sh`
- View API docs: `http://localhost:8000/docs`

---

## 🎉 Next Steps

After successful integration:

1. **Enhance Responses**
   - Add rich media (images, videos)
   - Use interactive buttons
   - Create message templates

2. **Analytics**
   - Track user engagement
   - Monitor conversion rates
   - A/B test responses

3. **Automation**
   - Auto-respond to common queries
   - Schedule follow-ups
   - Send application status updates

4. **Integration**
   - Connect to CRM
   - Sync with application database
   - Integrate payment gateway

---

**Last Updated:** Feb 12, 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅
