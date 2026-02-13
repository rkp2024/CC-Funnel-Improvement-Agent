# Jupiter Edge+ Card AI Agent

An AI-powered conversational agent for re-engaging users who drop off during the Jupiter Edge+ CSB Bank RuPay Credit Card application process.

## Features

- **Open Source LLM**: Uses DeepSeek-R1, Mistral-7B, or other models from Hugging Face for natural conversations
- **Multilingual Support**: Responds in English, Hindi, or Hinglish based on user's language
- **RAG System**: Retrieves relevant information about the Jupiter Edge+ card using Sentence Transformers
- **Conversation Management**: Tracks conversation state and dynamically handles user objections
- **FOMO Offers**: Configurable limited-time offers to re-engage hesitant customers
- **Interactive Demo**: Gradio web interface for easy interaction

## Prerequisites

### Quick Start (No prerequisites)
- You can use **TinyLlama** without any Hugging Face account or token

### For Better Quality (Recommended)

1. **Hugging Face Account**: Sign up at [huggingface.co](https://huggingface.co)
2. **Model Access** (choose one):
   - **Llama-3** (RECOMMENDED): Request access to [Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)
   - **Llama-2**: Request access to [Llama-2-7b-chat-hf](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)
   - Approval is usually instant
3. **Access Token**: Create a token at [Hugging Face Settings > Access Tokens](https://huggingface.co/settings/tokens)

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd "Funnel Expert"
```

2. **Install dependencies**:
```bash
pip install -r requirements-huggingface.txt
```

3. **Run the application**:
```bash
python3 app.py
```

## Usage

### 1. Setup (First Time)

When you first run the application, go to the **🔧 Setup** tab:

1. Paste your Hugging Face token (starts with `hf_...`)
2. Click "Initialize Agent"
3. Wait for the model to download (this may take a few minutes the first time)
4. You'll see "✅ Agent initialized successfully!" when ready

**Alternative: Environment Variable**

You can also set your token as an environment variable instead:

```bash
export HF_TOKEN=hf_your_token_here
python3 app.py
```

### 2. Start a New Conversation

Go to the **💬 Start New Conversation** tab:

1. Enter the customer's name
2. Select the drop-off stage where they abandoned their application
3. Click "Start Conversation"
4. Copy the User ID displayed for later use

### 3. Continue a Conversation

Go to the **🔄 Continue Conversation** tab:

1. Paste the User ID from the previous step
2. Type your message
3. Click "Send Message"

### 4. View Active Conversations

Go to the **📋 Active Conversations** tab to see all active conversations and their details.

## Multilingual Support

The agent automatically detects and responds in the user's preferred language:

### Supported Languages

1. **English** - Full support for all features
2. **Hindi (हिंदी)** - Full support in Devanagari script
3. **Hinglish** - Hindi written in English script (e.g., "Kya card lifetime free hai?")

### How It Works

- The agent automatically detects the language from the user's message
- Responses are provided in the same language for better user experience
- If a user asks in Hindi/Hinglish, the agent responds in Hinglish
- For unsupported languages, the agent politely informs the user

### Example Conversations

**English:**
```
User: Why do I need PAN card?
Agent: Great question! PAN Card is mandatory for credit card applications 
       in India as per RBI regulations...
```

**Hinglish:**
```
User: PAN card kyun chahiye?
Agent: Bahut accha sawal! PAN Card credit card ke liye zaroori hai kyunki 
       yeh RBI ka rule hai...
```

**Unsupported Language:**
```
User: [Question in French/Spanish/etc.]
Agent: I can only communicate in English, Hindi, or Hinglish. 
       Please ask your question in one of these languages.
```

## Drop-off Stages

The agent can handle conversations for users who dropped off at:

- PAN Card Confirmation
- Eligibility Check
- Card CVP (Customer Value Proposition)
- Personal Details Form
- Card Approval and Limit Assignment
- eKYC Process
- vKYC Process
- OTP Screen

 Running on local URL:  http://0.0.0.0:7860
* To create a public link, set `share=True` in `launch()`.
## FOMO (Fear of Missing Out) Offers

The agent includes a configurable FOMO system to re-engage hesitant customers:

### When FOMO Offers are Triggered

- User shows hesitation ("maybe", "let me think", "not sure")
- User wants to compare or check other options
- User declines to continue

### Configuring FOMO Offers

1. Go to the **🎁 FOMO Offers** tab
2. Choose from preset templates:
   - **Default**: ₹500 Jewels bonus (48-hour offer)
   - **High Value**: ₹1,000 Jewels premium welcome bonus
   - **Zero Fee Highlight**: Limited lifetime free card slots
   - **Instant Approval**: 2-hour instant approval window
3. Customize the offer message, urgency text, and call-to-action
4. Set how many times the offer can be shown per conversation
5. Click "Save Configuration"

### Example FOMO Offer

When a user says "I'm not sure" or "Let me think about it", the agent responds:

```
🎁 Limited Time Offer

Since you're one of our early applicants, we're offering an EXCLUSIVE bonus: 
Get ₹500 worth of Jewels (₹100 cashback) credited instantly on your first 
transaction! This offer is valid only for applications completed in the next 48 hours.

⏰ This exclusive bonus expires in 48 hours!

Don't miss out on this limited-time bonus. Would you like to complete your application now?

💳 Continue here: https://jupiter.money/edge-plus-upi-rupay-credit-card/
```

## Architecture

### RAG Engine (`app/rag_engine.py`)

- Loads card data from `app/data/card_data.json`
- Generates embeddings using Sentence Transformers (`all-mpnet-base-v2`)
- Performs semantic search to retrieve relevant information

### Agent Engine (`app/agent_engine.py`)

- Manages conversation state and history
- Generates context-aware responses using Llama-3 (or Llama-2/TinyLlama)
- Dynamically detects user intent and objections
- Provides stage-specific guidance

### Demo Application (`app.py`)

- Gradio-based web interface
- Handles user interactions and displays conversations
- Manages multiple concurrent conversations

## Card Data

All information about the Jupiter Edge+ CSB Bank RuPay Credit Card is stored in `app/data/card_data.json`, including:

- Cashback rates and limits
- Rewards program
- UPI features
- EMI features
- Eligibility criteria
- Fees and charges
- Application process details

## File Structure

```
Funnel Expert/
├── app/
│   ├── agent_engine.py      # Agent implementation with Llama-2
│   ├── data/
│   │   ├── card_data.json   # Card information
│   │   └── conversations/   # Saved conversations
│   ├── models.py            # Data models
│   └── rag_engine.py        # RAG implementation
├── app.py                   # Gradio demo application
├── README.md                # This file
└── requirements-huggingface.txt  # Dependencies
```

## Troubleshooting

### "Access to model is restricted"

Make sure you:
1. Requested access to your chosen model:
   - [Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) (recommended)
   - [Llama-2-7b-chat-hf](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)
2. Waited for approval (usually instant)
3. Used the correct token with read access

### "Agent not initialized"

Go to the **🔧 Setup** tab and initialize the agent with your Hugging Face token first.

### Out of memory errors

Large models require significant GPU memory:
- **Llama-3-8B**: ~16GB GPU memory
- **Llama-2-7B**: ~14GB GPU memory
- **TinyLlama-1.1B**: ~2GB GPU memory

If you don't have a GPU or enough memory:
- The model will automatically fall back to CPU (slower but works)
- Consider using **TinyLlama** from the dropdown (no token required)

## Deployment

### 🚀 Deploy to Replit (Recommended)

Replit is the easiest way to deploy this application!

**Quick Start:**

1. Go to [replit.com](https://replit.com)
2. Click **"+ Create Repl"** → **"Import from GitHub"**
3. Paste your repository URL
4. Add `HF_TOKEN` in Secrets (🔒 icon)
5. Click **"Run"** - Done! 🎉

**Why Replit?**
- ✅ Free tier with 500MB RAM (good for TinyLlama)
- ✅ No complex configuration
- ✅ Always-on option with Replit Core ($7/month)
- ✅ Better for ML apps than traditional hosting

See [REPLIT_DEPLOYMENT.md](REPLIT_DEPLOYMENT.md) for complete guide with troubleshooting.

### Alternative Deployment Options

**Hugging Face Spaces** (Best for ML, Free GPU):
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Create new Space (Gradio SDK)
3. Upload project files
4. Add HF_TOKEN in Space settings

**Heroku** (More expensive, see [DEPLOYMENT.md](DEPLOYMENT.md)):
- Requires Standard-2X dyno or higher ($50+/month)
- Better suited for non-ML applications

## License

This project is for demonstration purposes.

## Support

For issues or questions, please open an issue in the repository.
