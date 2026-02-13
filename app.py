import os
import uuid
import gradio as gr
import random
from datetime import datetime
from typing import Dict, Any, List

from app.models import FunnelType, CardType, DropOffStep, ObjectionType
from app.agent_engine import AgentEngine
from app import config
from app.rag_engine import RAGEngine

# RAG engine and agent will be initialized when user clicks "Initialize Agent"
rag_engine = None
agent = None

# Store active conversations
active_conversations = {}


def initialize_agent(model_choice: str, hf_token: str) -> str:
    """Initialize the agent with Hugging Face Inference API"""
    global agent, rag_engine
    
    # Model mapping - All run on HF servers via API (no download!)
    model_map = {
        "DeepSeek R1 8B ⭐ RECOMMENDED": {
            "name": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
            "requires_token": True,
            "description": "Best quality, runs on HF servers",
            "url": "https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
        },
        "Llama 3.1 8B (Excellent quality)": {
            "name": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "requires_token": True,
            "description": "High quality, fast API",
            "url": "https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct"
        },
        "Mistral 7B (Fast & reliable)": {
            "name": "mistralai/Mistral-7B-Instruct-v0.3",
            "requires_token": True,  # API requires token
            "description": "Good balance of speed and quality",
            "url": "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3"
        },
        "Qwen 2.5 7B (Multilingual)": {
            "name": "Qwen/Qwen2.5-7B-Instruct",
            "requires_token": True,  # API requires token
            "description": "Great for Hindi/Hinglish support",
            "url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct"
        }
    }
    
    # Validate HF token (required for Inference API)
    if not hf_token or not hf_token.strip():
        return "❌ Hugging Face token is required!\n\nGet your free token at: https://huggingface.co/settings/tokens"
    
    if not hf_token.startswith("hf_"):
        return "❌ Invalid token format. HF tokens start with 'hf_'\n\nCheck your token at: https://huggingface.co/settings/tokens"
    
    try:
        # Initialize RAG engine
        if rag_engine is None:
            try:
                rag_engine = RAGEngine()
            except Exception as e:
                return f"❌ Error initializing RAG engine: {str(e)}"
        
        # Get model info
        model_info = model_map.get(model_choice)
        if not model_info:
            return f"❌ Unknown model choice: {model_choice}"
        
        # Initialize agent with Inference API
        agent = AgentEngine(
            model_name=model_info["name"],
            rag_engine=rag_engine,
            hf_token=hf_token
        )
        
        model_name = model_choice.split(" (")[0]
        return f"""✅ Agent initialized successfully!

🤖 Model: {model_name}
📡 API Mode: Running on Hugging Face servers
💾 Local Storage: 0 MB (no download needed!)

You can now start conversations in the Chat tab. 🚀"""
        
    except ValueError as e:
        # Token or authentication error
        return f"❌ {str(e)}"
    except Exception as e:
        error_msg = f"❌ Error initializing agent: {str(e)}"
        
        if "rate limit" in str(e).lower():
            error_msg += "\n\n⚠️ Rate limit exceeded. Wait a moment and try again."
        elif "not found" in str(e).lower() or "does not exist" in str(e).lower():
            model_info = model_map.get(model_choice)
            if model_info and "llama" in model_info["name"].lower():
                error_msg += f"\n\n🔒 Llama models require approval. Request access at:\n{model_info['url']}"
            else:
                error_msg += "\n\n⚠️ Model not available. Try a different model."
        elif "connect" in str(e).lower() or "timeout" in str(e).lower():
            error_msg += "\n\n⚠️ Connection error. Check your internet connection."
        
        return error_msg

def create_test_event(name: str, drop_off_step: DropOffStep) -> Dict[str, Any]:
    """Create a test event for the agent"""
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    # Generate context based on drop-off step
    context = {
        "drop_off_step": drop_off_step,
        "last_activity": datetime.now().isoformat(),
        "days_in_funnel": random.randint(1, 7),
        "previous_sessions": random.randint(1, 3),
        "device_type": random.choice(["android", "ios"]),
        "app_version": "3.4.2"
    }
    
    # Add step-specific context
    if drop_off_step == DropOffStep.PAN_CARD_CONFIRMATION:
        context.update({
            "pan_status": random.choice(["pending", "invalid"]),
            "pan_entry_attempts": random.randint(1, 3)
        })
    elif drop_off_step == DropOffStep.ELIGIBILITY_CHECK:
        context.update({
            "income_entered": random.choice([True, False]),
            "credit_score_range": random.choice(["650-700", "700-750", "750+"])
        })
    
    event = {
        "user_id": user_id,
        "name": name,
        "phone": f"+91{9000000000 + random.randint(1000000, 9999999)}",
        "funnel_type": FunnelType.CREDIT_CARD,
        "card_type": CardType.EDGE_PLUS_RUPAY,
        "drop_off_step": drop_off_step,
        "objection_type": random.choice(list(ObjectionType)),
        "context": context
    }
    
    return event

def start_new_chat(name: str, drop_off_step: str):
    """Start a new conversation with the agent"""
    global agent
    
    if agent is None:
        return [[None, "❌ Please initialize the agent first in the Setup tab."]], "", gr.update(choices=list(active_conversations.keys()))
    
    # Convert drop_off_step string to enum
    step_enum = None
    for step in DropOffStep:
        if step.value == drop_off_step:
            step_enum = step
            break
    
    if not step_enum:
        return [[None, f"Error: Invalid drop-off step: {drop_off_step}"]], "", gr.update(choices=list(active_conversations.keys()))
    
    # Create test event
    event = create_test_event(name, step_enum)
    user_id = event["user_id"]
    
    # Start conversation
    response = agent.start_conversation(event)
    
    # Store conversation (keep dict format for internal tracking)
    active_conversations[user_id] = {
        "name": name,
        "drop_off_step": drop_off_step,
        "history": [{"role": "assistant", "content": response["message"]}],
        "user_id": user_id
    }
    
    # Return in Gradio Chatbot format: list of [user_msg, bot_msg] tuples
    return [[None, response["message"]]], user_id, gr.update(choices=list(active_conversations.keys()), value=user_id)

def send_message(message: str, history: List, user_id: str):
    """Process a user message and get agent response"""
    global agent
    
    if agent is None:
        history.append([None, "❌ Please initialize the agent first in the Setup tab."])
        return history, ""
    
    if not user_id or user_id not in active_conversations:
        history.append([None, "❌ Please start a new conversation first."])
        return history, ""
    
    if not message.strip():
        return history, ""
    
    # Store in internal format (dict)
    active_conversations[user_id]["history"].append({"role": "user", "content": message})
    
    # Process message
    response = agent.process_message(user_id, message)
    
    # Store agent response in internal format (dict)
    active_conversations[user_id]["history"].append({"role": "assistant", "content": response["message"]})
    
    # Add to Gradio history in tuple format [user_msg, bot_msg]
    history.append([message, response["message"]])
    
    # Return the updated history and clear input
    return history, ""

def load_conversation(user_id: str):
    """Load an existing conversation"""
    if user_id and user_id in active_conversations:
        # Convert internal dict format to Gradio tuple format
        history_dicts = active_conversations[user_id]["history"]
        gradio_history = []
        
        i = 0
        while i < len(history_dicts):
            msg = history_dicts[i]
            if msg["role"] == "assistant":
                # Bot message without user message
                gradio_history.append([None, msg["content"]])
                i += 1
            elif msg["role"] == "user":
                # User message, check if there's a bot response
                user_msg = msg["content"]
                bot_msg = None
                if i + 1 < len(history_dicts) and history_dicts[i + 1]["role"] == "assistant":
                    bot_msg = history_dicts[i + 1]["content"]
                    i += 2
                else:
                    i += 1
                gradio_history.append([user_msg, bot_msg])
            else:
                i += 1
        
        return gradio_history, user_id
    return [], ""

def list_conversations() -> List[Dict[str, Any]]:
    """List all active conversations"""
    return [
        {
            "user_id": user_id,
            "name": data["name"],
            "drop_off_step": data["drop_off_step"],
            "message_count": len(data["history"])
        }
        for user_id, data in active_conversations.items()
    ]

def get_current_fomo_config():
    """Get current FOMO offer configuration"""
    offer = config.FOMO_OFFERS.get(config.ACTIVE_FOMO_OFFER, config.FOMO_OFFERS["default"])
    return (
        config.ACTIVE_FOMO_OFFER,
        offer["enabled"],
        offer["title"],
        offer["message"],
        offer["urgency_text"],
        offer["cta"],
        config.FOMO_TRIGGER_CONDITIONS["max_attempts"]
    )

def update_fomo_config(offer_type, enabled, title, message, urgency_text, cta, max_attempts):
    """Update FOMO offer configuration"""
    try:
        # Update the config
        config.ACTIVE_FOMO_OFFER = offer_type
        config.FOMO_OFFERS[offer_type]["enabled"] = enabled
        config.FOMO_OFFERS[offer_type]["title"] = title
        config.FOMO_OFFERS[offer_type]["message"] = message
        config.FOMO_OFFERS[offer_type]["urgency_text"] = urgency_text
        config.FOMO_OFFERS[offer_type]["cta"] = cta
        config.FOMO_TRIGGER_CONDITIONS["max_attempts"] = max_attempts
        
        # Save to file
        config_content = f"""# Configuration for Jupiter Edge+ AI Agent

# FOMO (Fear of Missing Out) Offer Configuration
# This offer is shown when customers are hesitant or not willing to continue

FOMO_OFFERS = {repr(config.FOMO_OFFERS)}

# Choose which offer to use
ACTIVE_FOMO_OFFER = "{config.ACTIVE_FOMO_OFFER}"

# Trigger conditions - when to show FOMO offer
FOMO_TRIGGER_CONDITIONS = {repr(config.FOMO_TRIGGER_CONDITIONS)}

# App link for continuing application
APPLICATION_LINK = "{config.APPLICATION_LINK}"
"""
        
        with open("app/config.py", "w") as f:
            f.write(config_content)
        
        return "✅ FOMO offer configuration updated successfully!"
    except Exception as e:
        return f"❌ Error updating configuration: {str(e)}"

def load_offer_preset(offer_type):
    """Load a preset offer configuration"""
    offer = config.FOMO_OFFERS.get(offer_type, config.FOMO_OFFERS["default"])
    return (
        offer["enabled"],
        offer["title"],
        offer["message"],
        offer["urgency_text"],
        offer["cta"]
    )

# Define the Gradio interface
with gr.Blocks(title="Jupiter Edge+ Card Agent") as demo:
    gr.Markdown("# 💳 Jupiter Edge+ AI Re-engagement Agent")
    gr.Markdown("An AI agent that helps users complete their Jupiter Edge+ Credit Card application")
    
    # Store current user_id in state
    current_user_id = gr.State("")
    
    with gr.Tab("🔧 Setup"):
        gr.Markdown("## Initialize AI Agent with HF Inference API")
        gr.Markdown("""
        ### 🚀 **NEW: API Mode - No Model Downloads!**
        
        All models now run on **Hugging Face servers** via their Inference API:
        - ✅ **No downloads** - Models stay on HF servers
        - ✅ **No memory issues** - Works on any computer
        - ✅ **Instant startup** - No loading time
        - ✅ **Latest models** - Always up-to-date
        
        ### 🎯 Available Models:
        
        **DeepSeek R1 8B** ⭐ - Cutting-edge reasoning model, best quality
        **Llama 3.1 8B** - Meta's latest, excellent all-around
        **Mistral 7B** - Fast and reliable
        **Qwen 2.5 7B** - Best for Hindi/Hinglish support
        
        ### 🔑 **HF Token Required** (Free):
        
        1. Go to [Hugging Face Settings > Access Tokens](https://huggingface.co/settings/tokens)
        2. Click "New token" → Name it (e.g., "jupiter-agent") → Select "Read" access
        3. Copy the token and paste it below
        4. For gated models (Llama), request access first on the model page
        
        ### 💡 Which Model to Choose?
        
        - **Best quality**: DeepSeek R1 8B or Llama 3.1 8B
        - **Hindi/Hinglish**: Qwen 2.5 7B
        - **Fastest API**: Mistral 7B
        
        ---
        
        **⚠️ Connection Issues?**
        
        - Ensure you have internet access
        - Check if HF token is valid
        - Disable VPN if needed
        - Check if your firewall/proxy is blocking huggingface.co
        - Try using mobile hotspot if on corporate network
        - Enable "Bypass SSL" checkbox below
        """)
        
        with gr.Row():
            model_choice = gr.Dropdown(
                label="Choose Model (Runs on HF Servers - No Download!)",
                choices=[
                    "DeepSeek R1 8B ⭐ RECOMMENDED",
                    "Llama 3.1 8B (Excellent quality)",
                    "Mistral 7B (Fast & reliable)",
                    "Qwen 2.5 7B (Multilingual)"
                ],
                value="DeepSeek R1 8B ⭐ RECOMMENDED"
            )
        
        with gr.Row():
            hf_token_input = gr.Textbox(
                label="Hugging Face Token (only for gated models like Llama-3)",
                placeholder="hf_... (leave empty for most models)",
                type="password"
            )
        
        with gr.Row():
            init_btn = gr.Button("🚀 Initialize Agent", variant="primary", size="lg")
        
        with gr.Row():
            status_output = gr.Textbox(label="Status", interactive=False, lines=6)
        
        init_btn.click(
            fn=initialize_agent,
            inputs=[model_choice, hf_token_input],
            outputs=[status_output]
        )
    
    with gr.Tab("💬 Chat"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Start New Conversation")
                name_input = gr.Textbox(
                    label="Customer Name",
                    placeholder="Enter customer name",
                    value="Test User"
                )
                
                drop_off_options = [step.value for step in DropOffStep]
                drop_off_input = gr.Dropdown(
                    label="Drop-off Stage", 
                    choices=drop_off_options,
                    value=drop_off_options[0]
                )
                
                start_new_btn = gr.Button("🆕 Start New Chat", variant="primary", size="lg")
                
                gr.Markdown("---")
                gr.Markdown("### Or Load Existing")
                
                conversation_selector = gr.Dropdown(
                    label="Select Conversation",
                    choices=list(active_conversations.keys()),
                    interactive=True
                )
                
                load_btn = gr.Button("📂 Load Conversation", size="sm")
                
                gr.Markdown("---")
                
                user_id_display = gr.Textbox(
                    label="Current User ID",
                    interactive=False,
                    placeholder="No active conversation"
                )
            
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500
                )
                
                with gr.Row():
                    message_input = gr.Textbox(
                        label="Your Message",
                        placeholder="Type your message here...",
                        scale=4
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
        
        # Event handlers
        start_new_btn.click(
            fn=start_new_chat,
            inputs=[name_input, drop_off_input],
            outputs=[chatbot, current_user_id, conversation_selector]
        ).then(
            fn=lambda x: x,
            inputs=[current_user_id],
            outputs=[user_id_display]
        )
        
        load_btn.click(
            fn=load_conversation,
            inputs=[conversation_selector],
            outputs=[chatbot, current_user_id]
        ).then(
            fn=lambda x: x,
            inputs=[current_user_id],
            outputs=[user_id_display]
        )
        
        send_btn.click(
            fn=send_message,
            inputs=[message_input, chatbot, current_user_id],
            outputs=[chatbot, message_input]
        )
        
        message_input.submit(
            fn=send_message,
            inputs=[message_input, chatbot, current_user_id],
            outputs=[chatbot, message_input]
        )
    
    with gr.Tab("📊 Analytics"):
        gr.Markdown("### Active Conversations")
        conversations_output = gr.JSON(label="All Conversations")
        refresh_btn = gr.Button("🔄 Refresh")
        
        refresh_btn.click(
            fn=list_conversations,
            inputs=[],
            outputs=[conversations_output]
        )
    
    with gr.Tab("🎁 FOMO Offers"):
        gr.Markdown("## Configure FOMO (Fear of Missing Out) Offers")
        gr.Markdown("""
        FOMO offers are shown when customers are **hesitant, uncertain, or declining to continue**.
        
        These offers create urgency and give customers an extra reason to complete their application now.
        
        **When FOMO offers are triggered:**
        - Customer says "maybe", "let me think", "not sure", etc.
        - Customer wants to "compare", "check other options"
        - Customer declines to continue
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Select Offer Template")
                offer_preset = gr.Dropdown(
                    label="Choose Offer Template",
                    choices=list(config.FOMO_OFFERS.keys()),
                    value=config.ACTIVE_FOMO_OFFER
                )
                load_preset_btn = gr.Button("📥 Load Template", size="sm")
        
        with gr.Row():
            fomo_enabled = gr.Checkbox(
                label="Enable FOMO Offer",
                value=True
            )
            fomo_max_attempts = gr.Number(
                label="Max Times to Show per Conversation",
                value=config.FOMO_TRIGGER_CONDITIONS["max_attempts"],
                minimum=1,
                maximum=3
            )
        
        fomo_title = gr.Textbox(
            label="Offer Title",
            placeholder="e.g., 🎁 Limited Time Offer",
            lines=1
        )
        
        fomo_message = gr.Textbox(
            label="Offer Message",
            placeholder="Describe the exclusive offer...",
            lines=4
        )
        
        fomo_urgency = gr.Textbox(
            label="Urgency Text",
            placeholder="e.g., ⏰ This exclusive bonus expires in 48 hours!",
            lines=2
        )
        
        fomo_cta = gr.Textbox(
            label="Call-to-Action",
            placeholder="e.g., Would you like to complete your application now?",
            lines=2
        )
        
        with gr.Row():
            save_fomo_btn = gr.Button("💾 Save Configuration", variant="primary", size="lg")
        
        fomo_status = gr.Textbox(label="Status", interactive=False, lines=2)
        
        # Load current config on start
        demo.load(
            fn=get_current_fomo_config,
            inputs=[],
            outputs=[offer_preset, fomo_enabled, fomo_title, fomo_message, fomo_urgency, fomo_cta, fomo_max_attempts]
        )
        
        # Load preset when selected
        load_preset_btn.click(
            fn=load_offer_preset,
            inputs=[offer_preset],
            outputs=[fomo_enabled, fomo_title, fomo_message, fomo_urgency, fomo_cta]
        )
        
        # Save configuration
        save_fomo_btn.click(
            fn=update_fomo_config,
            inputs=[offer_preset, fomo_enabled, fomo_title, fomo_message, fomo_urgency, fomo_cta, fomo_max_attempts],
            outputs=[fomo_status]
        )
    
    # Tab 4: Logs & Analytics
    with gr.Tab("📊 Logs & Analytics"):
        gr.Markdown("""
        # 📊 Conversation Logs & Analytics
        
        View and analyze all chat interactions for insights and model improvement.
        """)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📈 Analytics Summary")
                refresh_analytics_btn = gr.Button("🔄 Refresh Analytics", variant="primary")
                analytics_display = gr.JSON(label="Analytics Summary")
                
                gr.Markdown("### 📋 Recent Conversations")
                refresh_logs_btn = gr.Button("🔄 Refresh Logs", variant="secondary")
                log_limit = gr.Slider(minimum=10, maximum=100, value=20, step=10, label="Number of recent logs")
                logs_display = gr.JSON(label="Recent Chat Logs")
            
            with gr.Column():
                gr.Markdown("### 💾 Export Options")
                
                gr.Markdown("**Export for Fine-tuning**")
                gr.Markdown("Download logs in OpenAI fine-tuning format")
                export_finetuning_btn = gr.Button("📥 Export Fine-tuning Data", variant="primary")
                finetuning_status = gr.Textbox(label="Status", interactive=False)
                
                gr.Markdown("**Export CSV**")
                gr.Markdown("Download all logs as CSV")
                export_csv_btn = gr.Button("📥 Export CSV", variant="primary")
                csv_status = gr.Textbox(label="Status", interactive=False)
                
                gr.Markdown("### 🔍 Search Logs")
                search_user_id = gr.Textbox(label="Search by User ID", placeholder="Enter user ID")
                search_user_btn = gr.Button("🔍 Search User Logs")
                user_logs_display = gr.JSON(label="User's Conversation Logs")
        
        # Functions for Logs & Analytics tab
        def get_analytics():
            """Get analytics summary"""
            try:
                if agent and hasattr(agent, 'logger') and agent.logger:
                    summary = agent.logger.get_analytics_summary()
                    return summary if summary else {"message": "No analytics data available yet. Start chatting to generate logs!"}
                else:
                    return {"message": "Agent not initialized or logging disabled"}
            except Exception as e:
                return {"error": f"Failed to get analytics: {str(e)}"}
        
        def get_recent_logs(limit):
            """Get recent log entries"""
            try:
                if agent and hasattr(agent, 'logger') and agent.logger:
                    logs = agent.logger.get_recent_logs(int(limit))
                    return logs if logs else [{"message": "No logs available yet. Start chatting to generate logs!"}]
                else:
                    return [{"message": "Agent not initialized or logging disabled"}]
            except Exception as e:
                return [{"error": f"Failed to get logs: {str(e)}"}]
        
        def export_for_finetuning():
            """Export logs for fine-tuning"""
            try:
                if agent and hasattr(agent, 'logger') and agent.logger:
                    output_file = agent.logger.export_for_finetuning()
                    return f"✅ Fine-tuning data exported to: {output_file}\n\nYou can download this file from the Repl's file browser."
                else:
                    return "❌ Agent not initialized or logging disabled"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def export_csv_logs():
            """Export logs as CSV"""
            try:
                if agent and hasattr(agent, 'logger') and agent.logger:
                    csv_path = agent.logger.export_csv()
                    return f"✅ CSV exported to: {csv_path}\n\nYou can download this file from the Repl's file browser."
                else:
                    return "❌ Agent not initialized or logging disabled"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def search_user_logs(user_id):
            """Search logs by user ID"""
            try:
                if not user_id:
                    return [{"message": "Please enter a user ID"}]
                    
                if agent and hasattr(agent, 'logger') and agent.logger:
                    logs = agent.logger.get_logs_by_user(user_id)
                    return logs if logs else [{"message": f"No logs found for user: {user_id}"}]
                else:
                    return [{"message": "Agent not initialized or logging disabled"}]
            except Exception as e:
                return [{"error": f"Failed to search logs: {str(e)}"}]
        
        def clear_all_logs():
            """Clear all logs - use with caution!"""
            try:
                if agent and hasattr(agent, 'logger') and agent.logger:
                    agent.logger.clear_logs()
                    return "✅ All logs have been cleared!"
                else:
                    return "❌ Agent not initialized or logging disabled"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        # Connect buttons to functions
        refresh_analytics_btn.click(
            fn=get_analytics,
            outputs=[analytics_display]
        )
        
        refresh_logs_btn.click(
            fn=get_recent_logs,
            inputs=[log_limit],
            outputs=[logs_display]
        )
        
        export_finetuning_btn.click(
            fn=export_for_finetuning,
            outputs=[finetuning_status]
        )
        
        export_csv_btn.click(
            fn=export_csv_logs,
            outputs=[csv_status]
        )
        
        search_user_btn.click(
            fn=search_user_logs,
            inputs=[search_user_id],
            outputs=[user_logs_display]
        )

# Launch the app
if __name__ == "__main__":
    # Get port from environment variable (AWS default: 8080)
    port = int(os.environ.get("PORT", 8080))
    
    # Launch with server settings for AWS deployment
    demo.launch(
        server_name="0.0.0.0",  # Allow external connections
        server_port=port,  # Use environment PORT or default 8080
        share=False,  # Don't create a share link when deployed
        show_error=True,
        debug=False  # Disable debug mode in production
    )