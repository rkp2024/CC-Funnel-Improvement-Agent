"""
FastAPI Application for WhatsApp Integration
Exposes Jupiter Edge+ Credit Card Agent via REST API and WebHooks

Author: Jupiter Money Team
Date: Feb 2026
"""

from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import json
import hmac
import hashlib
import logging
import uuid
from datetime import datetime
from app.agent_engine import AgentEngine
from app.models import Conversation, AgentState, DropOffStep

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Jupiter Edge+ Credit Card Agent API",
    description="REST API and WebHook for WhatsApp integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent Engine
try:
    agent_engine = AgentEngine()
    logger.info("✅ Agent Engine initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Agent Engine: {str(e)}")
    agent_engine = None

# Environment Configuration
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "jupiter_edge_plus_2026")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
API_KEY = os.getenv("API_KEY", "jupiter_api_key_2026")

# In-memory session store (use Redis in production)
session_store: Dict[str, Dict[str, Any]] = {}


# ==================== Pydantic Models ====================

class InitConversationRequest(BaseModel):
    """Request model for initializing conversation"""
    user_id: str = Field(..., description="Unique user identifier (phone number or UUID)")
    user_name: Optional[str] = Field(None, description="User's name")
    drop_off_step: Optional[str] = Field(None, description="Application step where user dropped off (e.g., 'pan_verification', 'document_upload')")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "919876543210",
                "user_name": "Rahul",
                "drop_off_step": "pan_verification",
                "metadata": {"source": "whatsapp", "campaign": "summer2026"}
            }
        }


class ChatRequest(BaseModel):
    """Request model for user response to bot"""
    user_id: str = Field(..., description="Unique user identifier (phone number or UUID)")
    message: str = Field(..., description="User's response message")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "919876543210",
                "message": "Yes, I want to continue my application"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoints"""
    success: bool
    user_id: str
    message: str
    intent: Optional[str] = None
    language: Optional[str] = None
    timestamp: str
    session_id: Optional[str] = None


class WebhookVerification(BaseModel):
    """Model for webhook verification"""
    mode: str
    challenge: str
    verify_token: str


class WhatsAppMessage(BaseModel):
    """WhatsApp message format"""
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    text: Dict[str, str]
    type: str = "text"


class WhatsAppWebhookPayload(BaseModel):
    """WhatsApp webhook payload structure"""
    object: str
    entry: List[Dict[str, Any]]


class ResetRequest(BaseModel):
    """Request to reset user session"""
    user_id: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    agent_initialized: bool
    version: str


# ==================== Helper Functions ====================

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify WhatsApp webhook signature for security
    """
    if not WHATSAPP_APP_SECRET:
        logger.warning("⚠️ WHATSAPP_APP_SECRET not set, skipping signature verification")
        return True
    
    try:
        expected_signature = hmac.new(
            WHATSAPP_APP_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"❌ Signature verification error: {str(e)}")
        return False


def verify_api_key(api_key: Optional[str]) -> bool:
    """
    Verify API key for general endpoints
    """
    if not API_KEY:
        return True  # No API key required if not set
    return api_key == API_KEY


def extract_whatsapp_message(payload: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Extract message details from WhatsApp webhook payload
    """
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return None
        
        message = messages[0]
        
        return {
            "user_id": message.get("from"),
            "message_id": message.get("id"),
            "message_text": message.get("text", {}).get("body", ""),
            "timestamp": message.get("timestamp"),
            "name": value.get("contacts", [{}])[0].get("profile", {}).get("name", "User")
        }
    except (IndexError, KeyError) as e:
        logger.error(f"❌ Error extracting WhatsApp message: {str(e)}")
        return None


def format_response_for_whatsapp(response: str, user_id: str) -> Dict[str, Any]:
    """
    Format agent response for WhatsApp Business API
    """
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": user_id,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": response
        }
    }


async def process_message_async(user_id: str, message: str, user_name: str = "User"):
    """
    Process message asynchronously (for background tasks)
    """
    try:
        if not agent_engine:
            return "Sorry, the service is temporarily unavailable. Please try again later."
        
        response = agent_engine.process_message(user_id, message)
        return response.get("message", "I'm here to help with your Jupiter Edge+ Credit Card!")
    except Exception as e:
        logger.error(f"❌ Error processing message: {str(e)}")
        return "Sorry, I encountered an error. Please try again."


# ==================== API Endpoints ====================

@app.get("/", response_class=PlainTextResponse)
async def root():
    """Root endpoint"""
    return "Jupiter Edge+ Credit Card Agent API - Running ✅"


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy" if agent_engine else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        agent_initialized=agent_engine is not None,
        version="1.0.0"
    )


@app.get("/webhook")
async def verify_webhook(
    request: Request,
    mode: str = None,
    challenge: str = None,
    verify_token: str = None
):
    """
    WhatsApp webhook verification endpoint (GET)
    
    This is called by WhatsApp to verify your webhook URL
    """
    logger.info(f"📞 Webhook verification request: mode={mode}, token={verify_token}")
    
    if mode == "subscribe" and verify_token == WHATSAPP_VERIFY_TOKEN:
        logger.info("✅ Webhook verified successfully")
        return PlainTextResponse(content=challenge, status_code=200)
    else:
        logger.warning("❌ Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def handle_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    WhatsApp webhook endpoint (POST)
    
    Receives messages from WhatsApp Business API
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Verify signature (security)
        if WHATSAPP_APP_SECRET and x_hub_signature_256:
            if not verify_webhook_signature(body, x_hub_signature_256):
                logger.warning("⚠️ Invalid webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        payload = json.loads(body)
        logger.info(f"📨 Received webhook payload: {json.dumps(payload, indent=2)}")
        
        # Extract message
        message_data = extract_whatsapp_message(payload)
        
        if not message_data:
            # No message to process (could be status update)
            return JSONResponse(content={"status": "ok"}, status_code=200)
        
        user_id = message_data["user_id"]
        message_text = message_data["message_text"]
        user_name = message_data["name"]
        
        logger.info(f"👤 Message from {user_name} ({user_id}): {message_text}")
        
        # Check if agent is initialized
        if not agent_engine:
            logger.error("❌ Agent engine not initialized")
            return JSONResponse(
                content={"status": "error", "message": "Service unavailable"},
                status_code=503
            )
        
        # Process message
        response = agent_engine.process_message(user_id, message_text)
        response_text = response.get("message", "I'm here to help!")
        
        logger.info(f"🤖 Response to {user_id}: {response_text[:100]}...")
        
        # Note: In production, you would send the response back to WhatsApp
        # using the WhatsApp Business API client
        # For now, we just log it and return success
        
        return JSONResponse(
            content={
                "status": "success",
                "response": response_text,
                "whatsapp_payload": format_response_for_whatsapp(response_text, user_id)
            },
            status_code=200
        )
        
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"❌ Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/init", response_model=ChatResponse)
async def init_conversation(
    request: InitConversationRequest,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Initialize conversation and get bot's first message
    
    This endpoint starts a new conversation for a user. The bot sends the first message
    based on the user's drop-off step (where they left in the application funnel).
    
    Headers:
        X-API-Key: Your API key (if configured)
    
    Body:
        {
            "user_id": "919876543210",
            "user_name": "Rahul",
            "drop_off_step": "pan_verification",
            "metadata": {"source": "whatsapp"}
        }
    
    Returns:
        Bot's contextual greeting message based on drop-off step
    """
    # Verify API key
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check agent initialization
    if not agent_engine:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    
    try:
        # Initialize conversation with user info and drop-off step
        if request.user_id in agent_engine.conversations:
            # Reset existing conversation
            del agent_engine.conversations[request.user_id]
        
        # Create new conversation
        drop_off = None
        if request.drop_off_step:
            try:
                drop_off = DropOffStep(request.drop_off_step)
            except:
                drop_off = None
        
        agent_engine.conversations[request.user_id] = Conversation(
            user_id=request.user_id,
            conversation_id=f"conv_{uuid.uuid4().hex[:12]}",
            state=AgentState.INIT,
            messages=[],
            user_info={
                "name": request.user_name or "User",
                "drop_off_step": drop_off
            }
        )
        
        # Generate bot's first message based on context
        response = agent_engine._generate_response(request.user_id)
        
        # Add bot's message to history
        agent_engine._add_message(request.user_id, "agent", response)
        
        # Detect language (default to English for init)
        detected_language = "ENGLISH"
        intent = "GREETING"
        
        logger.info(f"🆕 Init conversation - User: {request.user_id}, Drop-off: {request.drop_off_step}")
        
        return ChatResponse(
            success=True,
            user_id=request.user_id,
            message=response,
            intent=intent,
            language=detected_language,
            timestamp=datetime.utcnow().isoformat(),
            session_id=request.user_id
        )
        
    except Exception as e:
        logger.error(f"❌ Init conversation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Send user's response message to bot
    
    User responds to bot's message. Bot processes and returns next message.
    Conversation must be initialized first using /api/init endpoint.
    
    Headers:
        X-API-Key: Your API key (if configured)
    
    Body:
        {
            "user_id": "919876543210",
            "message": "Yes, I want to continue my application"
        }
    
    Returns:
        Bot's response to user's message
    """
    # Verify API key
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check agent initialization
    if not agent_engine:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    
    # Check if conversation exists
    if request.user_id not in agent_engine.conversations:
        raise HTTPException(
            status_code=404, 
            detail="Conversation not found. Please initialize conversation using /api/init endpoint first."
        )
    
    try:
        # Process user's message
        response = agent_engine.process_message(request.user_id, request.message)
        
        logger.info(f"💬 Chat - User: {request.user_id}, Message: {request.message[:50]}...")
        
        return ChatResponse(
            success=True,
            user_id=request.user_id,
            message=response.get("message", ""),
            intent=response.get("intent"),
            language=response.get("language"),
            timestamp=datetime.utcnow().isoformat(),
            session_id=request.user_id
        )
        
    except Exception as e:
        logger.error(f"❌ Chat API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reset")
async def reset_session(
    request: ResetRequest,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Reset user session/conversation
    
    Useful for testing or when user wants to start fresh
    """
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if not agent_engine:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    try:
        # Reset conversation
        if request.user_id in agent_engine.conversations:
            del agent_engine.conversations[request.user_id]
        
        logger.info(f"🔄 Reset session for user: {request.user_id}")
        
        return JSONResponse(
            content={
                "success": True,
                "message": f"Session reset for user {request.user_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"❌ Reset error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{user_id}")
async def get_session(
    user_id: str,
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Get user session information
    
    Returns conversation history and user state
    """
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if not agent_engine:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    conversation = agent_engine.conversations.get(user_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return JSONResponse(
        content={
            "user_id": user_id,
            "user_info": conversation.get("user_info", {}),
            "conversation_count": len(conversation.get("messages", [])),
            "last_message": conversation.get("messages", [])[-1] if conversation.get("messages") else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.get("/api/stats")
async def get_stats(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Get API statistics
    
    Returns active sessions and usage metrics
    """
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if not agent_engine:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    return JSONResponse(
        content={
            "active_sessions": len(agent_engine.conversations),
            "total_conversations": sum(
                len(conv.get("messages", [])) 
                for conv in agent_engine.conversations.values()
            ),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"❌ Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 API Server starting up...")
    logger.info(f"📍 Documentation available at: http://localhost:8000/docs")
    logger.info(f"🔐 API Key required: {bool(API_KEY)}")
    logger.info(f"🔒 WhatsApp webhook token: {WHATSAPP_VERIFY_TOKEN}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("🛑 API Server shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
