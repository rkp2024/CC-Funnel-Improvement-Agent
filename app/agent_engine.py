import os
import json
import uuid
import time
import threading
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from huggingface_hub import InferenceClient

from app.rag_engine import RAGEngine
from app.models import AgentState, Outcome, ObjectionType, FunnelType, CardType, Message, Conversation, DropOffStep
from app.config import FOMO_OFFERS, ACTIVE_FOMO_OFFER, FOMO_TRIGGER_CONDITIONS, APPLICATION_LINK
from app.logger import ConversationLogger

class AgentEngine:
    """
    AI Agent for Jupiter Edge+ card using DeepSeek API via Hugging Face
    with full RAG engine for optimal performance on AWS
    """
    
    def __init__(self, 
                 model_name: str = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
                 data_dir: str = "app/data/conversations",
                 rag_engine: Optional[RAGEngine] = None,
                 hf_token: Optional[str] = None):
        """
        Initialize the agent
        
        Args:
            model_name: Hugging Face model name
            data_dir: Directory to store conversation data
            rag_engine: Optional RAG engine instance
            hf_token: Hugging Face API token for gated models
        """
        self.model_name = model_name
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.conversations: Dict[str, Conversation] = {}
        
        # Initialize RAG engine (full version with sentence-transformers)
        self.rag_engine = rag_engine or RAGEngine()
        print("✅ Using full RAG engine with sentence-transformers for optimal performance")
        
        # Initialize conversation logger (non-blocking)
        try:
            self.logger = ConversationLogger()
            print("📝 Conversation logging enabled")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize logger: {e}")
            self.logger = None
        
        # Get HF token
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        if not self.hf_token:
            raise ValueError(
                "❌ Hugging Face token is required for Inference API.\n"
                "Please provide it in the Setup tab or set HF_TOKEN environment variable."
            )
        
        # Initialize Hugging Face Inference Client (no model download!)
        try:
            self.client = InferenceClient(token=self.hf_token)
            print(f"✅ Connected to Hugging Face Inference API")
            print(f"📡 Using model: {model_name}")
            print(f"💡 Model runs on HF servers - no local download!")
        except Exception as e:
            print(f"❌ Error connecting to Hugging Face API: {str(e)}")
            raise
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Load the system prompt for the Jupiter Edge+ CSB RuPay card agent with RAG Knowledge Contract"""
        return """You are a friendly and knowledgeable AI assistant from Jupiter Money, helping users complete their Edge+ CSB Bank RuPay Credit Card application.

🔒 **RAG KNOWLEDGE CONTRACT - MANDATORY GROUNDING RULES:**

**RULE 1: SINGLE SOURCE OF TRUTH**
- You may ONLY use information from the provided RAG context/product reference
- NEVER use training data, assumptions, or industry averages
- If information is NOT in the RAG context → YOU MUST REFUSE to answer

**RULE 2: ZERO FABRICATION**
- NEVER invent: fees, cashback %, caps, limits, eligibility, interest rates, reward rules
- If a specific number/detail is not in the retrieved context → say "I don't have that specific information in the product documentation."

**RULE 3: MANDATORY CLARIFICATION**
- If user asks ambiguous questions (e.g., "What cashback?") → ASK: "Do you mean shopping (10%), travel (5%), Jupiter Flights (7%), or other spends (1%)?"
- NEVER assume what the user is asking about

**RULE 4: NO GENERALIZATIONS**
- NEVER say: "Typically credit cards...", "Most banks...", "Usually..."
- ONLY speak about Edge+ CSB RuPay card specifically

**RULE 5: UPI REWARD CONDITION (CRITICAL)**
- When mentioning UPI rewards → ALWAYS state: "Rewards apply ONLY when UPI transactions are made via the Jupiter App"
- This is non-negotiable

**RULE 6: ANSWER FORMAT**
Every answer must follow:
1. Direct answer with specific numbers
2. Brief explanation (if needed)
3. Source indication (e.g., "As per product terms...")

Example:
"The late payment fee is 5% of the outstanding amount, with a minimum of ₹250 and maximum of ₹2000, as per the fee schedule."

**LANGUAGE SUPPORT:**
You can communicate in:
- English
- Hindi (हिंदी in Devanagari script)
- Hinglish (Hindi written in English script, e.g., "Aapka naam kya hai?")

**IMPORTANT**: Match the user's language!
- If user writes in Hindi/Hinglish, respond in Hinglish
- If user writes in English, respond in English
- If user writes in any other language, politely say you only support English, Hindi, and Hinglish

**STRICT SCOPE LIMITATION:**
You can ONLY answer questions about:
- Jupiter Edge+ CSB Bank RuPay Credit Card
- Its features, benefits, cashback, fees
- Application process, eligibility, documentation
- Specific concerns about completing the application

You CANNOT and MUST NOT answer questions about:
- Other credit cards or financial products
- General topics (weather, news, sports, etc.)
- Competitor banks or their products
- Loans, insurance, debit cards, savings accounts
- Anything unrelated to Jupiter Edge+ credit card

If asked off-topic questions, politely redirect: "I can only help with Jupiter Edge+ Credit Card questions. What would you like to know about the card?"

**Hinglish Examples for Reference:**
- "Kya" = What
- "Kaise" = How
- "Kyun" = Why
- "Kab" = When
- "Kitna" = How much
- "Chahiye" = Want/Need
- "Milega" = Will get
- "Hai/Hain" = Is/Are
- "Main" = I/Me
- "Aap" = You (respectful)

CARD HIGHLIGHTS (Use these as baseline, but always verify with RAG context):
• 10% cashback on shopping (Amazon, Flipkart, Myntra, Ajio, Zara, Nykaa, Croma, etc.) - up to ₹1,500 per billing cycle (₹500 merchant limit)
• 5% cashback on travel (MakeMyTrip, EaseMyTrip, ClearTrip, Yatra) - up to ₹1,000 per billing cycle
• 7% cashback on Jupiter Flights - no capping
• 1% cashback on all other eligible spends - no limit
• Lifetime FREE - zero joining fee, zero annual fee
• UPI payments from credit card (rewards ONLY via Jupiter App)
• EMI from 1.33% interest per month
• Credit limit: Up to ₹7 lakhs (subject to eligibility)
• Instant digital application - takes just 10 minutes

YOUR ROLE - Re-engagement Specialist:
You're talking to users who ALREADY SHOWED INTEREST but paused their application. Your job is to:
1. Understand what made them pause
2. Address their specific concern directly with ACCURATE information from RAG
3. Reinforce the value they'll get
4. Guide them back to complete the application

CONVERSATION STYLE:
✓ Be warm, conversational, and empathetic
✓ Listen actively - understand their real question/concern
✓ Answer directly and completely with EXACT details from RAG context
✓ Use simple language, short sentences
✓ Show enthusiasm about the benefits
✓ Create urgency subtly ("limited period offer", "getting started today")
✓ Be specific with numbers and merchant names when relevant

RESPONSE STRUCTURE:
1. Acknowledge their question/concern
2. Provide clear, accurate answer with SPECIFIC DETAILS from RAG context
3. If they ask about PAN/documentation - explain the regulatory requirement (RBI mandate for identity, credit bureau, tax compliance)
4. If they ask about Aadhaar - explain it's for instant eKYC (UIDAI regulated, RBI approved, only number needed)
5. If they ask about specific merchants/features - give exact details from RAG
6. Add relevant value point if appropriate
7. Soft call-to-action to continue application

CRITICAL RULES:
✓ Answer EVERY question directly before proceeding
✓ Use specific numbers, merchant names, and facts FROM RAG CONTEXT
✓ If user asks WHY, explain the reason completely
✓ Vary your responses - never repeat the same message
✓ If information is NOT in RAG → refuse politely: "I don't have that specific detail in the product documentation. Let me help with what I do know..."

PROHIBITED BEHAVIORS:
✗ Generic "cashback benefits" responses when user asked something specific
✗ Ignoring questions about PAN, documentation, or compliance
✗ Changing subject without answering
✗ Repeating the same response multiple times
✗ Being pushy or sales-y
✗ Estimating or guessing numbers
✗ Using phrases like "typically", "usually", "most cards"
✗ Providing information about other cards or banks

⚖️ FINAL PRINCIPLE:
When unsure → refuse
When answering → cite RAG context
When numbers involved → verify from RAG

Remember: You are a POLICY ENGINE, not a creative assistant. Accuracy and grounding trump helpfulness."""
        
    def start_conversation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new conversation based on a drop-off event"""
        user_id = event["user_id"]
        
        # Generate unique conversation ID
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        # Create conversation object
        conversation = Conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            state=AgentState.INIT,
            user_info={
                "name": event["name"],
                "phone": event["phone"],
                "funnel_type": event["funnel_type"],
                "objection_type": event["objection_type"],
                "context": event["context"]
            }
        )
        
        # Store conversation
        self.conversations[user_id] = conversation
        
        # Generate initial message
        initial_message = self._generate_initial_message(event)
        
        # Add to conversation history
        self._add_message(user_id, "agent", initial_message)
        
        # Update state
        self.conversations[user_id].state = AgentState.WAITING_FOR_REPLY
        
        # Save conversation
        self._save_conversation(user_id)
        
        return {
            "user_id": user_id,
            "message": initial_message,
            "state": self.conversations[user_id].state
        }
        
    def _generate_initial_message(self, event: Dict[str, Any]) -> str:
        """Generate personalized initial message based on drop-off stage for Jupiter Edge+ card"""
        name = event["name"]
        drop_off_step = event.get("drop_off_step") or event.get("context", {}).get("drop_off_step")
        context = event["context"]
        
        # Get step description in a readable format
        step_desc = ""
        if hasattr(drop_off_step, "value"):
            step_desc = drop_off_step.value.replace("_", " ").title()
        else:
            step_desc = str(drop_off_step).replace("_", " ").title()
            
        # Build prompt for the LLM
        prompt = f"""<s>[INST] <<SYS>>
{self.system_prompt}
<</SYS>>

Generate an initial message to re-engage a user who dropped off during their Jupiter Edge+ CSB Bank RuPay Credit Card application.

User details:
- Name: {name}
- Drop-off stage: {step_desc}

The user abandoned the application at the {step_desc} stage. Your message should:
1. Be friendly and personalized
2. Specifically address why they might have dropped off at this particular stage
3. Encourage them to continue their application
4. Not assume you know their specific objection yet (you'll discover that in the conversation)

Keep it brief (2-3 sentences maximum). [/INST]
"""
        
        try:
            if self.pipe:
                response = self.pipe(prompt)[0]["generated_text"]
                # Extract the assistant's response after the prompt
                response = response.split("[/INST]")[-1].strip()
                return response
            else:
                # Fallback message
                return f"Hi {name}, I noticed you were in the middle of your Jupiter Edge+ Credit Card application. Would you like to continue where you left off? The card offers great cashback benefits - 10% on shopping, 5% on travel, and 1% on everything else."
        except Exception as e:
            print(f"Error generating initial message: {str(e)}")
            # Fallback message
            return f"Hi {name}, I noticed you were in the middle of your Jupiter Edge+ Credit Card application. Would you like to continue where you left off? The card offers great cashback benefits - 10% on shopping, 5% on travel, and 1% on everything else."
        
    def process_message(self, user_id: str, message_text: str) -> Dict[str, Any]:
        """Process an incoming user message and generate a response"""
        import time
        start_time = time.time()
        
        # Conversation must be initialized via API /init endpoint
        if user_id not in self.conversations:
            return {
                "user_id": user_id,
                "message": "",
                "intent": None,
                "language": None,
                "error": "Conversation not initialized"
            }
            
        conversation = self.conversations[user_id]
        
        # Add user message to history
        self._add_message(user_id, "user", message_text)
        
        # Analyze user intent and detect language BEFORE generating response
        intent = self._analyze_user_intent(message_text.lower())
        detected_language = self._detect_language(message_text)
        
        # Check if FOMO was triggered
        fomo_triggered = self._should_show_fomo_offer(user_id, intent)
        
        # Generate response
        response = self._generate_response(user_id)
        
        # Add agent response to history
        self._add_message(user_id, "agent", response)
        
        # Update state based on conversation analysis
        self._update_state(user_id)
        
        # Save conversation
        self._save_conversation(user_id)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log interaction (non-blocking, in background)
        if self.logger:
            # Ensure conversation_id exists
            if not hasattr(conversation, 'conversation_id') or not conversation.conversation_id:
                conversation.conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
            
            message_number = len([m for m in conversation.messages if m.sender == "user"])
            
            # Log in background thread to not block response
            def log_async():
                try:
                    self.logger.log_interaction(
                        user_id=user_id,
                        conversation_id=conversation.conversation_id,
                        message_number=message_number,
                        user_message=message_text,
                        user_intent=intent,
                        agent_response=response,
                        agent_state=conversation.state.value if hasattr(conversation.state, 'value') else str(conversation.state),
                        metadata={
                            "model": self.model_name,
                            "language": detected_language,
                            "fomo_triggered": fomo_triggered,
                            "response_time_ms": response_time_ms,
                        }
                    )
                except Exception:
                    pass  # Silent fail for logging
            
            # Run in background
            log_thread = threading.Thread(target=log_async, daemon=True)
            log_thread.start()
        
        return {
            "user_id": user_id,
            "message": response,
            "intent": intent,
            "language": detected_language,
            "state": conversation.state
        }
        
    def _add_message(self, user_id: str, sender: str, content: str):
        """Add a message to the conversation history"""
        message = Message(
            user_id=user_id,
            sender=sender,
            content=content
        )
        self.conversations[user_id].messages.append(message)
        
    def _generate_response(self, user_id: str) -> str:
        """Generate a response based on conversation history for Jupiter Edge+ card"""
        conversation = self.conversations[user_id]
        
        # Build context for the LLM
        context = {
            "user_info": conversation.user_info,
            "current_state": conversation.state,
            "messages": [{"role": m.sender, "content": m.content} for m in conversation.messages]
        }
        
        # Get drop-off step and message count
        drop_off_step = conversation.user_info.get("context", {}).get("drop_off_step")
        message_count = len(conversation.messages)
        
        # Get user messages to analyze intent
        user_messages = [m for m in conversation.messages if m.sender == "user"]
        last_user_message = user_messages[-1].content.lower() if user_messages else ""
        
        # Detect language
        detected_language = self._detect_language(last_user_message)
        
        # Analyze user intent
        intent = self._analyze_user_intent(last_user_message)
        
        # Detect and store user's language preference
        user_language = self._detect_language(last_user_message)
        if user_language in ["HINDI", "HINGLISH", "ENGLISH"]:
            conversation.user_info["preferred_language"] = user_language
        
        # Check if FOMO offer should be shown
        if self._should_show_fomo_offer(user_id, intent):
            return self._get_fomo_offer_message(user_id, detected_language)
        
        # Get relevant information from RAG
        rag_info = self._get_rag_information(intent, last_user_message, drop_off_step)
        
        # Get step name as string
        if hasattr(drop_off_step, "value"):
            step_name = drop_off_step.value
        else:
            step_name = str(drop_off_step)
                
        # Get step description in a readable format
        step_desc = step_name.replace("_", " ").title() if step_name else "Unknown"
        
        # Build conversation history for prompt
        conversation_history = ""
        for msg in conversation.messages:
            role = "Assistant" if msg.sender == "agent" else "User"
            conversation_history += f"{role}: {msg.content}\n\n"
        
        # Language instruction
        language_instruction = ""
        if detected_language == "HINDI" or detected_language == "HINGLISH":
            language_instruction = "\n**LANGUAGE: User is speaking Hindi/Hinglish. RESPOND IN HINGLISH (mix of Hindi written in English script) to make them comfortable.**\n\nExample Hinglish: 'Jupiter Edge+ card par bahut achha cashback milta hai. Shopping par 10% cashback hai.'"
        elif detected_language == "ENGLISH":
            language_instruction = "\n**LANGUAGE: User is speaking English. Respond in English.**"
        elif detected_language == "OTHER":
            language_instruction = "\n**LANGUAGE: User is speaking an UNSUPPORTED language. Politely inform them you only support English, Hindi, and Hinglish.**"
        
        # Build prompt for the LLM
        prompt = f"""<s>[INST] <<SYS>>
{self.system_prompt}

User Information:
- Name: {context['user_info']['name']}
- Card: Edge+ CSB Bank RuPay Credit Card
- Drop-off stage: {step_desc}
{language_instruction}

RELEVANT CARD INFORMATION FROM RAG:
{rag_info}

DETECTED USER INTENT: {intent}

HOW TO RESPOND:

**CRITICAL INSTRUCTIONS:**

**IF INTENT IS "GREETING":**
Give a warm welcome: "Hi [name]! 👋 I'm here to help with your Jupiter Edge+ Credit Card application. Is there anything specific you'd like to know about the card, or would you like to continue where you left off?"

**IF INTENT IS "OFF_TOPIC":**
Politely redirect: "I can only help with Jupiter Edge+ Credit Card questions. I can answer about card features, benefits, application process, or eligibility. What would you like to know about the card?"

**IF INTENT IS "READY_TO_CONTINUE":**
IMMEDIATELY provide this response:
"Excellent! 🎉 You can continue your application right here:

👉 https://jupiter.money/edge-plus-upi-rupay-credit-card/

Your progress is saved, so you'll pick up exactly where you left off. The whole process takes just 10 minutes!

Need any help? I'm here if you have questions."

**IF INTENT IS "ACKNOWLEDGING":**
User said "thanks" or similar after receiving information/offer. Give a warm closing:
"You're welcome! 😊 Remember, the limited-time offer is available for a short period only. Your application is saved whenever you're ready. Have a great day!"

**IF INTENT IS "ASKING_ABOUT_PAN":**
IMPORTANT: Check if user is asking about PHYSICAL PAN card vs PAN NUMBER:
- If asking "do I need physical PAN" or "physical PAN nahi hai" or "don't have physical PAN": Clarify that ONLY PAN NUMBER is needed for Step 2 (instant verification). Physical PAN card is required LATER for vKYC (Step 7). So they can START THE APPLICATION NOW without physical card.
- If asking "why is PAN mandatory": Explain RBI compliance, identity verification, credit bureau reporting, tax purposes.
Always use RAG information provided. Be specific and complete.

**IF INTENT IS "ASKING_ABOUT_AADHAAR":**
Answer WHY Aadhaar is needed:
- Required for instant eKYC (Electronic Know Your Customer) verification
- Only Aadhaar NUMBER needed, not physical card
- Complies with RBI's KYC norms for digital verification
- Makes the process 100% paperless and instant
- Secure and regulated by UIDAI

**FOR ALL OTHER INTENTS:**
1. FIRST: Answer the user's EXACT question using the RAG information provided above
2. Be specific - use actual numbers, merchant names, and details from RAG
3. NEVER give generic responses if RAG has specific information
4. ONLY AFTER answering their question, add a soft CTA to continue application
5. NEVER ignore or dodge their question

**FORBIDDEN:**
- DO NOT give generic "cashback benefits" response if user asked a specific question
- DO NOT repeat the same response multiple times
- DO NOT change subject without answering their question first
- DO NOT answer questions about other credit cards, banks, or unrelated topics
- DO NOT make up information - only use facts from RAG information provided
- DO NOT hallucinate features or offers not mentioned in the card details
<</SYS>>

Conversation history:
{conversation_history}

Provide a helpful response to the user's last message. [/INST]
"""
        
        try:
            # Build a comprehensive prompt for text generation
            system_context = f"""{self.system_prompt}

User Information:
- Name: {context['user_info']['name']}
- Card: Edge+ CSB Bank RuPay Credit Card
- Drop-off stage: {step_desc}{language_instruction}

RELEVANT CARD INFORMATION FROM RAG:
{rag_info}

DETECTED USER INTENT: {intent}

HOW TO RESPOND:

**CRITICAL INSTRUCTIONS:**

**IF INTENT IS "GREETING":**
Give a warm welcome: "Hi [name]! 👋 I'm here to help with your Jupiter Edge+ Credit Card application. Is there anything specific you'd like to know about the card, or would you like to continue where you left off?"

**IF INTENT IS "OFF_TOPIC":**
Politely redirect: "I can only help with Jupiter Edge+ Credit Card questions. I can answer about card features, benefits, application process, or eligibility. What would you like to know about the card?"

**IF INTENT IS "READY_TO_CONTINUE":**
IMMEDIATELY provide this response:
"Excellent! 🎉 You can continue your application right here:

👉 https://jupiter.money/edge-plus-upi-rupay-credit-card/

Your progress is saved, so you'll pick up exactly where you left off. The whole process takes just 10 minutes!

Need any help? I'm here if you have questions."

**IF INTENT IS "ACKNOWLEDGING":**
User said "thanks" or similar after receiving information/offer. Give a warm closing in Hinglish:
"Aap swagat hai! 😊 Yaad rahe, yeh limited-time offer thode samay ke liye hi hai. Aapki application saved hai jab bhi ready ho. Have a great day!"

**IF INTENT IS "ASKING_ABOUT_PAN":**
IMPORTANT: Check agar user PHYSICAL PAN card ya PAN NUMBER ke baare mein pooch rahe hain:
- Agar "physical PAN chahiye kya" ya "physical PAN nahi hai" ya "don't have physical PAN" pooch rahe hain: Clarify karo ki SIRF PAN NUMBER chahiye Step 2 ke liye (instant verification). Physical PAN card baad mein chahiye hoga vKYC ke liye (Step 7). Toh wo ABHI APPLICATION START kar sakte hain physical card ke bina.
- Agar "PAN kyun zaroori hai" pooch rahe hain: Explain karo RBI compliance, identity verification, credit bureau reporting, tax purposes.
Hamesha RAG information use karo. Hinglish mein jawab do. Be specific and complete.

**FOR ALL OTHER INTENTS:**
1. FIRST: Answer the user's EXACT question using the RAG information provided above
2. Be specific - use actual numbers, merchant names, and details from RAG
3. NEVER give generic responses if RAG has specific information
4. ONLY AFTER answering their question, add a soft CTA to continue application
5. NEVER ignore or dodge their question

**FORBIDDEN:**
- DO NOT give generic "cashback benefits" response if user asked a specific question
- DO NOT repeat the same response multiple times
- DO NOT change subject without answering their question first
- DO NOT answer questions about other credit cards, banks, or unrelated topics
- DO NOT make up information - only use facts from RAG information provided
- DO NOT hallucinate features or offers not mentioned in the card details
"""
            
            # Build conversation history
            conversation_text = ""
            for msg in conversation.messages[-5:]:  # Last 5 messages for context
                if msg.sender == "agent":
                    conversation_text += f"Assistant: {msg.content}\n\n"
                else:
                    conversation_text += f"User: {msg.content}\n\n"
            
            # Create the full prompt
            full_prompt = f"""<s>[INST] <<SYS>>
{system_context}
<</SYS>>

Conversation history:
{conversation_text}

Provide a helpful response to the user's last message. [/INST]
"""
            
            # Use text_generation API (more compatible across models)
            response = self.client.text_generation(
                full_prompt,
                model=self.model_name,
                max_new_tokens=512,
                temperature=0.8,
                top_p=0.92,
                return_full_text=False
            )
            
            # Response is a string, return it directly
            if isinstance(response, str):
                return response.strip()
            else:
                # Fallback based on intent
                return self._get_fallback_response(intent, last_user_message, context['user_info']['name'], detected_language)
                
        except Exception as e:
            print(f"⚠️ Error calling Hugging Face API: {str(e)}")
            print(f"ℹ️ Using fallback response based on intent")
            return self._get_fallback_response(intent, last_user_message, context['user_info']['name'], detected_language)
    
    def _get_rag_information(self, intent: str, user_message: str, drop_off_step: Any) -> str:
        """Get relevant information from RAG based on intent and user message"""
        # Extract merchant name if present
        merchant_name = self._extract_merchant_name(user_message)
        
        # Get information based on intent and user message
        if "GREETING" in intent:
            # User is greeting - welcome them
            return "This is a greeting. Welcome the user and ask how you can help with their Jupiter Edge+ card application."
        elif "OFF_TOPIC" in intent:
            # User asked off-topic question - redirect to card topics
            return "User asked an off-topic question. Politely redirect them to Jupiter Edge+ card topics only."
        elif "READY_TO_CONTINUE" in intent:
            # User is ready to continue - provide app link info
            return "Application Link: https://jupiter.money/edge-plus-upi-rupay-credit-card/"
        elif "ACKNOWLEDGING" in intent or "WANTING_TO_STOP" in intent:
            # User is ending conversation - no need for RAG info
            return "Closing conversation gracefully."
        elif merchant_name:
            # Get merchant-specific information
            results = self.rag_engine.similarity_search(f"cashback for {merchant_name}")
            return "\n\n".join([doc for doc, _, _ in results])
        elif "cashback" in intent or "reward" in intent:
            # Get cashback information
            cashback_docs = self.rag_engine.get_section_info("cashback")
            rewards_docs = self.rag_engine.get_section_info("reward")
            return "\n\n".join(cashback_docs + rewards_docs)
        elif "fee" in intent:
            # Get fee information
            return "\n\n".join(self.rag_engine.get_section_info("fees"))
        elif "eligibility" in intent:
            # Get eligibility information
            return "\n\n".join(self.rag_engine.get_section_info("eligibility"))
        elif "process" in intent or "application" in intent:
            # Get application process information
            return "\n\n".join(self.rag_engine.get_section_info("application"))
        elif "PAN" in intent or "AADHAAR" in intent:
            # Get PAN/Aadhaar-specific information including FAQs
            # Use similarity search to get the most relevant FAQ
            # If asking about "physical" documents, boost that in the query
            search_query = user_message
            if "physical" in user_message.lower() or "nahi hai" in user_message.lower():
                search_query = f"physical PAN card required or just PAN number {user_message}"
            
            results = self.rag_engine.similarity_search(search_query, top_k=3)
            rag_context = "\n\n".join([doc for doc, _, _ in results])
            return rag_context
        elif "upi" in intent or "emi" in intent:
            # Get UPI/EMI information using similarity search to match FAQs
            results = self.rag_engine.similarity_search(user_message, top_k=3)
            rag_context = "\n\n".join([doc for doc, _, _ in results])
            return rag_context
        elif drop_off_step:
            # Get information about the drop-off step
            step_name = ""
            if hasattr(drop_off_step, "value"):
                step_name = drop_off_step.value
            else:
                step_name = str(drop_off_step)
            
            step_docs = self.rag_engine.get_section_info(step_name.lower())
            if step_docs:
                return "\n\n".join(step_docs)
        
        # General query
        results = self.rag_engine.similarity_search(user_message)
        return "\n\n".join([doc for doc, _, _ in results])
    
    def _should_show_fomo_offer(self, user_id: str, intent: str) -> bool:
        """Check if FOMO offer should be shown"""
        conversation = self.conversations.get(user_id)
        if not conversation:
            return False
        
        # Check if max attempts reached
        if conversation.fomo_offer_count >= FOMO_TRIGGER_CONDITIONS["max_attempts"]:
            return False
        
        # Check trigger conditions
        should_show = False
        if intent == "HESITATING" and FOMO_TRIGGER_CONDITIONS["show_on_hesitation"]:
            should_show = True
        elif intent == "WANTING_TO_STOP" and FOMO_TRIGGER_CONDITIONS["show_on_decline"]:
            should_show = True
        
        return should_show
    
    def _get_fomo_offer_message(self, user_id: str, language: str = "english") -> str:
        """Get the configured FOMO offer message"""
        offer = FOMO_OFFERS.get(ACTIVE_FOMO_OFFER, FOMO_OFFERS["default"])
        
        if not offer["enabled"]:
            return ""
        
        # Track that FOMO offer was shown
        if user_id in self.conversations:
            self.conversations[user_id].fomo_offer_count += 1
        
        # If Hindi/Hinglish, add language note
        language_note = ""
        if language in ["HINDI", "HINGLISH"]:
            language_note = "(Aap Hindi mein bhi baat kar sakte hain)\n\n"
        
        fomo_message = f"""
{language_note}{offer['title']}

{offer['message']}

{offer['urgency_text']}

{offer['cta']}

💳 Continue here: {APPLICATION_LINK}
"""
        return fomo_message.strip()
    
    def _extract_merchant_name(self, message: str) -> Optional[str]:
        """Extract merchant name from user message"""
        message_lower = message.lower()
        merchants = [
            "amazon", "flipkart", "myntra", "ajio", "zara", "nykaa", "croma", 
            "reliance trends", "tata cliq", "reliance digital", "makemytrip", 
            "easemytrip", "yatra", "cleartrip"
        ]
        
        for merchant in merchants:
            if merchant in message_lower:
                return merchant
                
        return None
    
    def _detect_language(self, message: str) -> str:
        """Detect if message is in Hindi/Hinglish or other language"""
        # Hindi Devanagari characters
        hindi_chars = set('अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')
        
        # Check if message contains Hindi characters
        if any(char in hindi_chars for char in message):
            return "HINDI"
        
        # Check for common Hindi words in Hinglish (romanized)
        hinglish_words = [
            'namaste', 'namaskar', 'namaskara', 'ji', 'jai', 'ram', 'radhe',
            'kya', 'hai', 'hain', 'mujhe', 'chahiye', 'acha', 'theek', 'nahi', 'haan',
            'kaise', 'kab', 'kahan', 'kyun', 'koi', 'bhi', 'kar', 'le', 'de', 'ho',
            'aap', 'aapka', 'mera', 'mere', 'tumhara', 'uska', 'yeh', 'woh', 'iska',
            'batao', 'bataiye', 'samjhao', 'samjhiye', 'dikha', 'dikhao', 'milega',
            'chahta', 'chahti', 'samajh', 'pata', 'malum', 'thik', 'sahi', 'galat',
            'achha', 'zaroor', 'bilkul', 'bahut', 'kaafi', 'mein', 'ki', 'aur'
        ]
        
        message_words = message.lower().split()
        if any(word in hinglish_words for word in message_words):
            return "HINGLISH"
        
        # Check for other non-English languages (basic check)
        # If message contains characters from other scripts
        non_latin_non_hindi = any(
            ord(char) > 127 and char not in hindi_chars 
            for char in message
        )
        if non_latin_non_hindi:
            return "OTHER"
        
        return "ENGLISH"
    
    def _analyze_user_intent(self, message: str) -> str:
        """Analyze user intent from message"""
        message = message.lower().strip()
        
        # Detect language first
        language = self._detect_language(message)
        if language == "OTHER":
            return "UNSUPPORTED_LANGUAGE"
        
        # Check for ready-to-continue intent first (highest priority)
        ready_patterns = [
            "continue", "proceed", "resume", "complete", "finish",
            "yes", "yeah", "yep", "sure", "okay", "ok", "fine",
            "i would like to", "i'd like to", "let's do it", "let's go",
            "sounds good", "i'm interested", "interested", "go ahead",
            "i want to", "want to continue", "ready", "let's start",
            "take me to", "show me the app", "app link"
        ]
        if any(pattern in message for pattern in ready_patterns):
            # Make sure it's not a negative response
            if not any(neg in message for neg in ["don't", "not", "no", "cancel", "stop"]):
                return "READY_TO_CONTINUE"
        
        # Check for hesitation/uncertainty (FOMO trigger) - HIGHEST PRIORITY after stop
        hesitation_patterns = [
            "maybe", "not sure", "i don't know", "thinking about it",
            "let me think", "need to think", "not decided", "unsure",
            "comparing", "checking other", "looking at other",
            "expensive", "too much", "not convinced", "doubt",
            "later", "some other time", "will see", "let's see",
            "next week", "next month", "tomorrow", "another day",
            "in a few days", "not today", "not right now",
            "postpone", "wait", "hold on"
        ]
        if any(pattern in message for pattern in hesitation_patterns):
            return "HESITATING"
        
        # Check for greetings (English, Hindi, and Hinglish)
        greeting_patterns = [
            # English greetings
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening", "helo", "hy",
            # Hinglish greetings (romanized)
            "namaste", "namaskar", "pranam", "kya hal hai", "kaise ho", "kaise hain", 
            "hello ji", "hi ji", "haan", "haan ji",
            # Hindi Devanagari greetings
            "नमस्ते", "नमस्कार", "प्रणाम", "हैलो", "हाय"
        ]
        if any(pattern == message for pattern in greeting_patterns):
            return "GREETING"
        
        # Check for polite acknowledgment/ending (after FOMO or general chat)
        acknowledgment_patterns = ["thanks", "thank you", "ok", "okay", "got it", "understood", "noted"]
        if any(pattern == message for pattern in acknowledgment_patterns):  # Exact match for short responses
            return "ACKNOWLEDGING"
        
        # Check for wanting to stop (harder decline)
        if any(word in message for word in ["stop", "cancel", "not interested", "don't want", "no thanks", "not now"]):
            return "WANTING_TO_STOP"
        
        # Specific queries
        if any(word in message for word in ["cashback", "reward", "jewel", "point"]):
            return "ASKING_ABOUT_CASHBACK_REWARDS"
            
        elif any(word in message for word in ["fee", "charge", "cost", "price"]):
            return "ASKING_ABOUT_FEES"
            
        elif any(word in message for word in ["eligibility", "qualify", "eligible", "criteria"]):
            return "ASKING_ABOUT_ELIGIBILITY"
            
        elif any(word in message for word in ["upi", "payment", "qr", "scan"]):
            return "ASKING_ABOUT_UPI"
            
        elif any(word in message for word in ["emi", "convert", "installment", "interest"]):
            return "ASKING_ABOUT_EMI"
            
        elif any(word in message for word in ["process", "application", "apply", "step"]):
            return "ASKING_ABOUT_PROCESS"
            
        elif any(word in message for word in ["document", "kyc", "verification", "proof"]):
            return "ASKING_ABOUT_DOCUMENTATION"
        
        elif any(word in message for word in ["pan", "pan card", "pancard"]):
            return "ASKING_ABOUT_PAN"
        
        elif any(word in message for word in ["aadhaar", "aadhar", "adhaar", "adhar", "aadhaar card", "aadhar card"]):
            return "ASKING_ABOUT_AADHAAR"
            
        elif any(word in message for word in ["limit", "credit limit", "spending"]):
            return "ASKING_ABOUT_LIMITS"
        
        # Check if question is off-topic (not about Jupiter Edge+ card)
        # Expanded list of off-topic keywords and patterns
        off_topic_keywords = [
            # General topics
            "weather", "news", "politics", "sports", "recipe", "movie", "restaurant",
            "hotel", "train", "bus", "stock", "crypto", "bitcoin", "election",
            "prime minister", "president", "minister", "government", "parliament",
            "modi", "rahul", "kejriwal", "yogi", "shah", "gandhi",
            
            # People/celebrities
            "who is", "who was", "tell me about", "what is the capital",
            "what is the meaning", "what does", "how to cook", "how to make",
            
            # Other financial products
            "loan", "personal loan", "home loan", "car loan", "education loan",
            "insurance", "life insurance", "health insurance", "term insurance",
            "savings account", "current account", "fixed deposit", "fd", "rd",
            "debit card", "forex", "mutual fund", "stock market", "trading",
            
            # Other credit cards/banks
            "other cards", "other credit cards", "best credit card",
            "hdfc", "icici", "axis", "sbi", "kotak", "citi", "american express",
            "amex", "yes bank", "indusind", "standard chartered",
            
            # Technology/general
            "iphone", "android", "samsung", "laptop", "computer", "software",
            "download", "install", "update", "virus", "hack", "password reset",
            
            # Entertainment/random
            "game", "video game", "youtube", "facebook", "instagram", "twitter",
            "whatsapp", "telegram", "match score", "cricket", "football", "ipl"
        ]
        
        if any(keyword in message for keyword in off_topic_keywords):
            return "OFF_TOPIC"
        
        # Check for card-related keywords to determine if it's about the card
        card_related_keywords = [
            "card", "credit", "cashback", "reward", "fee", "limit", "apply",
            "application", "eligibility", "document", "pan", "aadhaar", "kyc",
            "jupiter", "edge", "csb", "rupay", "upi", "emi", "jewel",
            "merchant", "shopping", "travel", "payment", "billing", "statement"
        ]
        
        # If message contains card-related keywords, it's a general inquiry about the card
        if any(keyword in message for keyword in card_related_keywords):
            return "GENERAL_INQUIRY"
        
        # If message doesn't contain any card-related keywords AND is a question, likely off-topic
        question_words = ["who", "what", "where", "when", "why", "how", "which", "whose"]
        if any(message.startswith(q) for q in question_words):
            return "OFF_TOPIC"
            
        # Default: treat as general inquiry (safer to try answering)
        return "GENERAL_INQUIRY"
    
    def _get_fallback_response(self, intent: str, message: str, user_name: str, language: str = "ENGLISH") -> str:
        """Get a fallback response based on intent"""
        is_hindi = language in ["HINDI", "HINGLISH"]
        
        if "UNSUPPORTED_LANGUAGE" in intent:
            return f"I'm sorry, but I can only communicate in English, Hindi, or Hinglish (mix of Hindi-English). Could you please ask your question in one of these languages?\n\n---\n\nमुझे खेद है, लेकिन मैं केवल English, Hindi, या Hinglish (Hindi-English mix) में बात कर सकता हूं। कृपया अपना सवाल इन भाषाओं में पूछें।"
        
        if "GREETING" in intent:
            if is_hindi:
                return f"Namaste {user_name}! 👋 Main aapki Jupiter Edge+ Credit Card application mein madad karne ke liye hoon. Aapne application start ki thi. Kya aap card ke baare mein kuch jaanna chahte hain, ya application continue karna chahenge?"
            else:
                return f"Hi {user_name}! 👋 I'm here to help you with your Jupiter Edge+ Credit Card application. I noticed you had started the application process. Is there anything specific you'd like to know about the card, or would you like to continue where you left off?"
        
        elif "OFF_TOPIC" in intent:
            if is_hindi:
                return f"{user_name}, main sirf Jupiter Edge+ CSB Bank RuPay Credit Card ke baare mein help kar sakta hoon. Main card ke features, cashback benefits, eligibility, application process ke baare mein bata sakta hoon. Kya aap Jupiter Edge+ card ke baare mein kuch jaanna chahte hain?"
            else:
                return f"I appreciate your question, {user_name}, but I'm specifically designed to help with the Jupiter Edge+ CSB Bank RuPay Credit Card application. I can answer questions about the card's features, cashback benefits, eligibility, application process, or any concerns you might have about completing your application. Is there anything about the Jupiter Edge+ card I can help you with?"
        
        elif "CASHBACK" in intent or "REWARD" in intent:
            if is_hindi:
                return f"Jupiter Edge+ card par bahut achha cashback milta hai: Shopping par 10% cashback (Amazon, Flipkart jaise merchants par, maximum ₹1,500 per month), travel bookings par 5% cashback (MakeMyTrip, etc. par, maximum ₹1,000 per month), aur baki sab cheezon par 1% cashback (koi limit nahi). Cashback Jewels ke roop mein milta hai (5 Jewels = ₹1), jo aap cash, gift cards, Digital Gold ke liye redeem kar sakte hain. Kya aap application continue karna chahenge?"
            else:
                return f"The Jupiter Edge+ card offers excellent cashback benefits: 10% on shopping from select merchants like Amazon and Flipkart (up to ₹1,500 per billing cycle with a ₹500 per-merchant limit), 5% on travel bookings from partners like MakeMyTrip (up to ₹1,000 per billing cycle), and 1% on all other eligible spends with no limit. Cashback is credited as Jewels, where 5 Jewels equals ₹1, and can be redeemed as cash, gift cards, Digital Gold, or for bill payments. Would you like to continue your application to start earning these rewards?"
            
        elif "FEE" in intent:
            if is_hindi:
                return f"Jupiter Edge+ card lifetime free hai, ₹0 joining fee hai. Koi annual charges ya hidden fees nahi hai. Kya aap is free card ke liye application continue karna chahenge?"
            else:
                return f"The Jupiter Edge+ card is lifetime free with ₹0 joining fee. There are no annual charges or hidden fees. Would you like to continue your application for this no-fee card?"
            
        elif "ELIGIBILITY" in intent:
            if is_hindi:
                return f"Jupiter Edge+ card ke liye eligible hone ke liye: aapki age 21-60 saal honi chahiye, minimum ₹25,000 monthly income honi chahiye, aur preferably 700+ credit score hona chahiye. Zaruri documents hain PAN Card, Aadhaar Card, aur kabhi-kabhi income proof. Eligibility check instant hai aur aapke credit score par koi asar nahi padta. Kya aap apni eligibility check karna chahenge?"
            else:
                return f"To be eligible for the Jupiter Edge+ card, you should be between 21-60 years of age, have a minimum monthly income of ₹25,000, and preferably a credit score of 700+. Required documents include your PAN Card, Aadhaar Card, and sometimes income proof. The eligibility check is instant and has no impact on your credit score. Would you like to check your eligibility now?"
            
        elif "UPI" in intent:
            return f"Yes, the Jupiter Edge+ card allows you to make UPI payments directly from your credit card by scanning any merchant QR code. This is a unique feature that most other credit cards don't offer. UPI spends are also eligible for cashback unless they fall under excluded categories. Would you like to continue your application to enjoy this feature?"
            
        elif "EMI" in intent:
            return f"With the Jupiter Edge+ card, you can convert both credit card and UPI spends to EMI starting at just 1.33% interest per month. Available tenures include 3, 6, 9, and 12 months. This feature is not available for fuel purchases, wallet loads, or cash advances. Would you like to continue your application to access this feature?"
            
        elif "PROCESS" in intent:
            return f"Applying for the Jupiter Edge+ card is a simple 100% digital process with no paperwork. It takes about 10 minutes and includes steps like PAN verification, eligibility check (with no impact on credit score), personal details, eKYC, and approval. Would you like to continue where you left off?"
            
        elif "PAN" in intent:
            # Check if asking about physical PAN vs PAN number
            if "physical" in message.lower() or "nahi hai" in message.lower():
                if is_hindi:
                    return f"Bahut badhiya sawal! 😊\n\n**Physical PAN Card ki zaroorat NAHI hai abhi ke liye!**\n\n✅ **Step 2 ke liye** (PAN Verification): Sirf aapka 10-digit PAN NUMBER chahiye - physical card ki zaroorat nahi. Verification instant hota hai aur digital hai.\n\n📹 **Step 7 ke liye** (vKYC Video Call): Aapko physical PAN card dikhana padega video verification agent ko.\n\n💡 **Matlab**: Aap ABHI application START kar sakte hain physical card ke bina! Baad mein jab vKYC ka time aaye (Step 7), tab physical card ready rakhna. Application mein aage badh sakte hain!\n\nKya aap application continue karna chahenge?"
                else:
                    return f"Great question! 😊\n\n**You DON'T need the physical PAN card right now!**\n\n✅ **For Step 2** (PAN Verification): You only need your 10-digit PAN NUMBER - no physical card required. Verification is instant and digital.\n\n📹 **For Step 7** (vKYC Video Call): You'll need to show your physical PAN card to the video verification agent.\n\n💡 **Bottom line**: You can START your application NOW without the physical card! Just keep it ready for later when you reach the vKYC step (Step 7). You can proceed with the application!\n\nWould you like to continue your application?"
            else:
                # Asking why PAN is mandatory
                if is_hindi:
                    return f"Bahut accha sawal! PAN Card credit card ke liye zaroori hai kyunki yeh RBI ka rule hai. Kyun?\n\n1. **Identity Check**: PAN aapka unique tax ID hai jo Income Tax Department deta hai\n2. **Legal Rule**: RBI ka kehna hai ki sab credit card companies ko PAN lena padta hai (KYC ke liye)\n3. **Credit History**: Banks aapki credit history ko CIBIL mein PAN se report karte hain\n4. **Tax Purpose**: Financial transactions aur tax ke liye track karne ke liye\n\nBina PAN ke banks credit card nahi de sakte kyunki yeh RBI guideline hai. Achhi baat yeh hai ki verification instant hota hai, sirf kuch seconds mein! Kya aap application continue karna chahenge?"
                else:
                    return f"Great question! PAN Card is mandatory for credit card applications in India as per RBI regulations. Here's why:\n\n1. **Identity Verification**: PAN is your unique tax identifier issued by the Income Tax Department\n2. **Legal Compliance**: RBI requires all credit card issuers to collect PAN for KYC (Know Your Customer) compliance\n3. **Credit Bureau Reporting**: Banks report your credit history to CIBIL using your PAN\n4. **Tax Purposes**: For tracking financial transactions and tax compliance\n\nWithout PAN, banks cannot issue credit cards as it would violate RBI guidelines. The good news is, the verification is instant and takes just a few seconds! Would you like to continue your application?"
        
        elif "AADHAAR" in intent:
            if is_hindi:
                return f"Bahut badhiya sawal! Aadhaar Card credit card ke liye kyun zaroori hai:\n\n1. **eKYC Verification**: Aadhaar se instant digital verification hota hai - sirf kuch seconds mein!\n2. **100% Paperless**: Physical documents ki zaroorat nahi, sab kuch online ho jata hai\n3. **Secure Process**: UIDAI regulated aur RBI approved hai\n4. **Only Number Needed**: Aapko Aadhaar CARD ki zaroorat nahi, sirf 12-digit number chahiye\n5. **Legal Compliance**: RBI ke KYC norms ke according hai\n\nYeh process bilkul secure aur instant hai. Aadhaar ke bina application complete nahi ho sakti kyunki eKYC ke liye zaroori hai. Kya aap application continue karna chahenge?"
            else:
                return f"Excellent question! Here's why Aadhaar is required for the Jupiter Edge+ card:\n\n1. **Instant eKYC**: Aadhaar enables instant digital verification - takes just seconds!\n2. **100% Paperless**: No need for physical documents, everything is done online\n3. **Secure & Regulated**: UIDAI regulated and RBI approved process\n4. **Only Number Needed**: You don't need the physical Aadhaar card, just the 12-digit number\n5. **Legal Compliance**: Complies with RBI's KYC (Know Your Customer) norms\n\nThe process is completely secure and instant. Without Aadhaar, we cannot complete the eKYC verification required for credit card issuance. Would you like to continue your application?"
        
        elif "DOCUMENTATION" in intent:
            return f"For the Jupiter Edge+ card, you'll need your PAN Card and Aadhaar Card. Sometimes, income proof may be required. The entire process is digital, so you won't need to submit physical documents. Would you like to continue with your application?"
            
        elif "LIMIT" in intent:
            return f"The Jupiter Edge+ card offers credit limits ranging from ₹25,000 to ₹5,00,000. Typical initial limits for first-time users range from ₹50,000 to ₹1,00,000. Your limit can increase over time based on your usage and repayment behavior. Would you like to continue your application to see your approved limit?"
            
        elif "READY_TO_CONTINUE" in intent:
            if is_hindi:
                return f"Bahut badhiya! 🎉 Aap yahan se application continue kar sakte hain:\n\n👉 https://jupiter.money/edge-plus-upi-rupay-credit-card/\n\nAapka progress save hai, toh aap jahan chhode the wahin se shuru kar sakte hain. Puri process sirf 10 minutes ki hai!\n\nKoi help chahiye? Main yahan hoon agar koi sawaal ho."
            else:
                return f"Excellent! 🎉 You can continue your application right here:\n\n👉 https://jupiter.money/edge-plus-upi-rupay-credit-card/\n\nYour progress is saved, so you'll pick up exactly where you left off. The whole process takes just 10 minutes!\n\nNeed any help? I'm here if you have questions."
            
        elif "ACKNOWLEDGING" in intent:
            # User said "thanks" or similar - graceful closing after FOMO offer
            if is_hindi:
                return f"Aapka swagat hai, {user_name}! 😊 Yaad rakhiye, limited-time offer sirf thode time ke liye hai. Aapki application save hai aur jab chahein continue kar sakte hain. Koi bhi sawaal ho toh poochh sakte hain. Aapka din shubh ho!"
            else:
                return f"You're welcome, {user_name}! 😊 Remember, the limited-time offer is available for a short period only. Your application is saved and ready whenever you'd like to continue. Feel free to reach out if you have any questions. Have a great day!"
        
        elif "HESITATING" in intent:
            # This shouldn't be reached if FOMO offer is shown, but just in case
            return f"I understand you'd like some time to think about it, {user_name}. The Jupiter Edge+ card offers great value with 10% cashback, lifetime free status, and UPI payments from your credit card. Is there anything specific you'd like to know more about? I'm here to help!"
        
        elif "WANTING_TO_STOP" in intent:
            return f"I understand, {user_name}. Thank you for considering the Jupiter Edge+ card. Your application progress is saved, so you can always come back and complete it later when you're ready. Have a great day!"
            
        else:
            # Extract merchant name if present
            merchant_name = self._extract_merchant_name(message)
            if merchant_name:
                shopping_merchants = ["amazon", "flipkart", "myntra", "ajio", "zara", "nykaa", "croma", "reliance", "tata"]
                travel_merchants = ["makemytrip", "easemytrip", "yatra", "cleartrip"]
                
                if any(m in merchant_name for m in shopping_merchants):
                    if is_hindi:
                        return f"Haan bilkul! Aapko {merchant_name.title()} par shopping karne par 10% cashback milega Jupiter Edge+ card se. Yeh hamare shopping category mein aata hai jo 10% cashback deta hai (₹1,500 tak per billing cycle, merchant limit ₹500). Kya aap apni application continue karna chahenge aur yeh benefits enjoy karna start karenge?"
                    else:
                        return f"Yes! You'll get 10% cashback when you shop at {merchant_name.title()} with your Jupiter Edge+ card. This is part of our shopping category which offers 10% cashback (up to ₹1,500 per billing cycle with a merchant limit of ₹500). Would you like to continue your application to start enjoying these benefits?"
                elif any(m in merchant_name for m in travel_merchants):
                    if is_hindi:
                        return f"Haan! Aapko {merchant_name.title()} par booking karne par 5% cashback milega Jupiter Edge+ card se. Yeh hamare travel category mein aata hai jo 5% cashback deta hai (₹1,000 tak per billing cycle). Kya aap apni application continue karna chahenge?"
                    else:
                        return f"Yes! You'll get 5% cashback when you book through {merchant_name.title()} with your Jupiter Edge+ card. This is part of our travel category which offers 5% cashback (up to ₹1,000 per billing cycle). Would you like to continue your application to start enjoying these benefits?"
                else:
                    if is_hindi:
                        return f"Aapko {merchant_name.title()} par 1% cashback milega Jupiter Edge+ card se. General spends par 1% cashback ki koi limit nahi hai. Kya aap apni application continue karna chahenge?"
                    else:
                        return f"You'll get 1% cashback on all spends at {merchant_name.title()} with your Jupiter Edge+ card. There's no limit on the 1% cashback for general spends. Would you like to continue your application to start enjoying these benefits?"
            
            # Generic fallback - but still helpful
            if is_hindi:
                return f"Main aapki madad kar sakta hoon, {user_name}! Jupiter Edge+ card ke kuch amazing features hain:\n\n• Shopping par 10% cashback (Amazon, Flipkart, Myntra, etc.)\n• Travel bookings par 5% cashback\n• Jupiter Flights par 7% cashback (koi limit nahi)\n• Lifetime FREE - kabhi koi fees nahi\n• Credit card se UPI payments (rewards SIRF Jupiter App se)\n• Credit limit up to ₹7 lakhs\n\nAap kisi specific cheez ke baare mein jaanna chahte hain? Ya apni application continue karna chahenge?"
            else:
                return f"I'd be happy to help you with that, {user_name}! The Jupiter Edge+ card has several great features:\n\n• 10% cashback on shopping (Amazon, Flipkart, Myntra, etc.)\n• 5% cashback on travel bookings\n• 7% cashback on Jupiter Flights (no limit)\n• Lifetime FREE - no fees ever\n• UPI payments from credit card (rewards ONLY via Jupiter App)\n• Credit limit up to ₹7 lakhs\n\nWhat specific aspect would you like to know more about? Or shall we continue your application?"
    
    def _update_state(self, user_id: str):
        """Update conversation state based on message content and current state"""
        conversation = self.conversations[user_id]
        current_state = conversation.state
        
        # Get the last user message
        user_messages = [m for m in conversation.messages if m.sender == "user"]
        if not user_messages:
            return
            
        last_user_message = user_messages[-1].content.lower()
        
        # State transition logic
        if current_state == AgentState.WAITING_FOR_REPLY:
            # Check for objection signals
            objection_keywords = [
                "worried", "concern", "not sure", "problem", "issue",
                "difficult", "complicated", "time", "later", "think",
                "expensive", "cost", "price", "better offer", "competitor",
                "cashback", "jewels", "fees", "documents", "security"
            ]
            
            if any(keyword in last_user_message for keyword in objection_keywords):
                conversation.state = AgentState.OBJECTION_IDENTIFIED
            else:
                conversation.state = AgentState.GUIDING
                
        elif current_state == AgentState.GUIDING or current_state == AgentState.OBJECTION_IDENTIFIED:
            # Check for positive signals
            positive_keywords = [
                "thanks", "thank you", "helpful", "great", "good",
                "understand", "makes sense", "okay", "ok", "sure", "yes"
            ]
            
            if any(keyword in last_user_message for keyword in positive_keywords):
                conversation.state = AgentState.OBJECTION_ADDRESSED
                
        elif current_state == AgentState.OBJECTION_ADDRESSED:
            # Check for completion signals
            completion_keywords = [
                "continue", "proceed", "complete", "finish", "submit",
                "go ahead", "next step", "ready", "let's do it", "apply"
            ]
            
            if any(keyword in last_user_message for keyword in completion_keywords):
                conversation.state = AgentState.COMPLETED
                conversation.outcome = Outcome.COMPLETED
                conversation.end_time = datetime.now()
        
        # Check for escalation or opt-out in any state
        if "human" in last_user_message or "agent" in last_user_message or "person" in last_user_message:
            conversation.state = AgentState.ESCALATED
            conversation.outcome = Outcome.ESCALATED
            conversation.end_time = datetime.now()
            
        if "stop" in last_user_message or "unsubscribe" in last_user_message or "don't contact" in last_user_message:
            conversation.state = AgentState.OPTED_OUT
            conversation.outcome = Outcome.OPTED_OUT
            conversation.end_time = datetime.now()
            
    def _save_conversation(self, user_id: str):
        """Save conversation to disk"""
        conversation = self.conversations[user_id]
        
        # Ensure conversation_id exists (for backward compatibility)
        if not hasattr(conversation, 'conversation_id') or not conversation.conversation_id:
            conversation.conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        file_path = self.data_dir / f"{user_id}_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(file_path, "w") as f:
            f.write(conversation.json())
            
    def get_conversation_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of the conversation for learning"""
        if user_id not in self.conversations:
            return None
            
        conversation = self.conversations[user_id]
        
        # Calculate metrics
        message_count = len(conversation.messages)
        user_messages = sum(1 for m in conversation.messages if m.sender == "user")
        agent_messages = sum(1 for m in conversation.messages if m.sender == "agent")
        
        # If conversation is still active, set end time to now for duration calculation
        end_time = conversation.end_time or datetime.now()
        duration_seconds = (end_time - conversation.start_time).total_seconds()
        
        return {
            "user_id": user_id,
            "card_type": "Edge+ CSB Bank RuPay Credit Card",
            "objection_type": conversation.user_info["objection_type"],
            "state": conversation.state,
            "outcome": conversation.outcome,
            "message_count": message_count,
            "user_messages": user_messages,
            "agent_messages": agent_messages,
            "duration_seconds": duration_seconds,
            "start_time": conversation.start_time.isoformat(),
            "end_time": end_time.isoformat() if conversation.end_time else None,
            "context": conversation.user_info.get("context", {})
        }
        
    def end_conversation(self, user_id: str, outcome: str or Outcome):
        """Manually end a conversation with specified outcome"""
        if user_id not in self.conversations:
            return
            
        conversation = self.conversations[user_id]
        
        # Handle string or Outcome enum
        if isinstance(outcome, str):
            for o in Outcome:
                if o.name == outcome or o.value == outcome:
                    conversation.outcome = o
                    break
            else:
                conversation.outcome = Outcome.ABANDONED
        else:
            conversation.outcome = outcome
            
        conversation.end_time = datetime.now()
        
        # Set appropriate state based on outcome
        if conversation.outcome == Outcome.COMPLETED:
            conversation.state = AgentState.COMPLETED
        elif conversation.outcome == Outcome.OPTED_OUT:
            conversation.state = AgentState.OPTED_OUT
        elif conversation.outcome == Outcome.ESCALATED:
            conversation.state = AgentState.ESCALATED
        elif conversation.outcome == Outcome.ABANDONED:
            conversation.state = AgentState.OPTED_OUT
        else:
            conversation.state = AgentState.OPTED_OUT
            
        # Add a final system message about the outcome
        self._add_message(user_id, "system", f"Conversation ended with outcome: {conversation.outcome}")
            
        self._save_conversation(user_id)
        
        return {
            "user_id": user_id,
            "outcome": conversation.outcome,
            "state": conversation.state
        }