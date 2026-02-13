# 🧪 Testing Guide for Jupiter Edge+ AI Agent

## 🚀 Application Status

```
✅ Status: RUNNING
🌐 URL: http://localhost:8080
🔢 PID: 41117
📚 RAG Documents: 50 (including 20 FAQs)
🌐 Languages: English, Hindi, Hinglish
🛡️ Off-Topic Detection: 60+ keywords
```

---

## 🧪 Test Suite

### 1️⃣ **Language Support Tests**

#### Test 1A: English Input
```
Input: "What is the cashback on shopping?"
Expected: Response in English
Example: "The Jupiter Edge+ card offers 10% cashback on shopping..."
```

#### Test 1B: Hinglish Input
```
Input: "Shopping par kitna cashback milta hai?"
Expected: Response in Hinglish
Example: "Jupiter Edge+ card par shopping ke liye 10% cashback milta hai..."
```

#### Test 1C: Hindi Script Input
```
Input: "मुझे PAN card की जरूरत है क्या?"
Expected: Response in Hinglish (romanized)
Example: "Haan, PAN card zaruri hai. Step 2 mein sirf PAN number chahiye..."
```

#### Test 1D: Unsupported Language (Spanish)
```
Input: "¿Cuál es el reembolso?"
Expected: Polite refusal
Example: "I can only communicate in English, Hindi, or Hinglish..."
```

#### Test 1E: Unsupported Language (Chinese)
```
Input: "什么是现金返还？"
Expected: Polite refusal
Example: "I can only communicate in English, Hindi, or Hinglish..."
```

---

### 2️⃣ **FAQ Retrieval Tests**

#### Test 2A: Physical PAN Question (CRITICAL)
```
Input: "Do I need a physical PAN card?"
OR: "Physical PAN card bhi lagega kya?"

Expected: Specific FAQ answer
"For the initial PAN verification (Step 2), you only need your 10-digit 
PAN number - no physical card required. However, during the vKYC process 
(Step 7), you will need to show your physical PAN card to the video 
verification agent."

Status: ✅ FIXED - Now uses similarity search to retrieve FAQ
```

#### Test 2B: Physical Aadhaar Question
```
Input: "Do I need physical Aadhaar card?"

Expected: Specific FAQ answer
"No, you do NOT need the physical Aadhaar card. You only need your 
12-digit Aadhaar number for the eKYC process."
```

#### Test 2C: UPI Rewards Question
```
Input: "Will I get UPI cashback with Google Pay?"
OR: "Can I use any UPI app?"

Expected: Must mention Jupiter App only
"You can make UPI payments using the Jupiter App or any other UPI app. 
However, cashback rewards are credited ONLY when UPI transactions are 
made via the Jupiter App."
```

#### Test 2D: Maximum Cashback Question
```
Input: "What is the maximum cashback I can earn?"

Expected: Detailed breakdown
"Shopping: Up to ₹1,500 per billing cycle (10% cashback with ₹500 
merchant limit). Travel: Up to ₹1,000 per billing cycle (5% cashback). 
Jupiter Flights: No limit (7% cashback). Others: No limit (1% cashback)."
```

#### Test 2E: Credit Limit Question
```
Input: "What is the maximum credit limit?"

Expected: ₹7 lakhs (not ₹5 lakhs)
"The credit limit ranges from ₹25,000 to ₹7,00,000 (7 lakhs) depending 
on your eligibility."
```

---

### 3️⃣ **Off-Topic Detection Tests**

#### Test 3A: Political Question
```
Input: "Who is Narendra Modi?"

Expected: Polite redirect
"I can only help with Jupiter Edge+ Credit Card questions. I can answer 
about card features, benefits, application process, or eligibility. What 
would you like to know about the card?"

Status: ✅ FIXED - Now detects "modi" as off-topic keyword
```

#### Test 3B: General "Who is" Question
```
Input: "Who is Virat Kohli?"

Expected: Polite redirect
Status: ✅ Should redirect (starts with "who is" + no card keywords)
```

#### Test 3C: Weather Question
```
Input: "What's the weather today?"

Expected: Polite redirect
Status: ✅ Should redirect ("weather" is off-topic keyword)
```

#### Test 3D: Other Bank Question
```
Input: "Is HDFC credit card better?"

Expected: Polite redirect
Status: ✅ Should redirect ("hdfc" is off-topic keyword)
```

---

### 4️⃣ **RAG Grounding Tests**

#### Test 4A: Fabrication Prevention
```
Input: "What is the lounge access benefit?"

Expected: Honest answer
"I don't have that specific information in the product documentation. 
The Edge+ card focuses on cashback rewards..."

Status: ✅ Should refuse/clarify (not in RAG data)
```

#### Test 4B: Ambiguous Question
```
Input: "What cashback do I get?"

Expected: Asks for clarification
"Do you mean shopping (10%), travel (5%), Jupiter Flights (7%), or other 
spends (1%)?"

Status: ⚠️ Depends on LLM following instructions
```

#### Test 4C: Specific Merchant Question
```
Input: "Do I get cashback on Amazon?"

Expected: Specific answer from RAG
"Yes! You'll get 10% cashback when you shop at Amazon with your Jupiter 
Edge+ card (up to ₹1,500 per billing cycle with a ₹500 merchant limit)."
```

---

### 5️⃣ **Product Data Accuracy Tests**

#### Test 5A: Jupiter Flights Cashback
```
Input: "What's the cashback on Jupiter Flights?"

Expected: 7% with no capping
"You get 7% cashback on flight bookings through Jupiter Flights with no 
capping limit."

Status: ✅ Updated in RAG
```

#### Test 5B: Card Replacement Fee
```
Input: "What if I lose my card?"

Expected: Mentions ₹249 fee
"You can instantly block it through the Jupiter app. A replacement card 
will be issued for a fee of ₹249."

Status: ✅ Updated in RAG
```

#### Test 5C: Late Payment Fee
```
Input: "What is the late payment fee?"

Expected: 5% with min/max
"The late payment fee is 5% of the outstanding amount due, subject to a 
minimum of ₹250 and a maximum of ₹2,000."

Status: ✅ Updated in RAG
```

---

## 📝 Test Results Template

| Test ID | Test Description | Input | Expected Result | Actual Result | Status |
|---------|------------------|-------|-----------------|---------------|--------|
| 1A | English Input | "What is cashback?" | English response | | ⬜ |
| 1B | Hinglish Input | "Cashback kitna hai?" | Hinglish response | | ⬜ |
| 2A | Physical PAN | "Physical PAN lagega?" | FAQ answer | | ⬜ |
| 3A | Off-topic | "Who is Modi?" | Redirect | | ⬜ |
| 4C | Amazon cashback | "Amazon par cashback?" | 10% details | | ⬜ |
| 5A | Jupiter Flights | "Jupiter Flights cashback?" | 7%, no cap | | ⬜ |

---

## 🎯 Priority Test Cases

### **MUST PASS:**
1. ✅ Physical PAN question → FAQ answer (not generic)
2. ✅ Off-topic question (Modi) → Redirect
3. ✅ UPI rewards → Must mention "Jupiter App only"
4. ✅ Credit limit → ₹7 lakhs (not ₹5 lakhs)

### **SHOULD PASS:**
1. ⭐ Hinglish input → Hinglish response
2. ⭐ Unsupported language → Polite refusal
3. ⭐ Ambiguous question → Asks for clarification
4. ⭐ Jupiter Flights → 7% no capping

### **NICE TO HAVE:**
1. 💫 Pure Hindi script → Hinglish response
2. 💫 Complex queries → Accurate breakdown
3. 💫 Multiple questions → Answers all parts

---

## 🔧 How to Test

### Step 1: Access Application
Open browser: `http://localhost:8080`

### Step 2: Initialize Agent
1. Go to **Setup** tab
2. Choose model: "DeepSeek R1 8B ⭐ RECOMMENDED"
3. Enter HF token (if required)
4. Click "Initialize Agent"
5. Wait for success message

### Step 3: Start Chat
1. Go to **Chat** tab
2. Enter name: "Test User"
3. Select drop-off stage: Any
4. Click "Start New Chat"

### Step 4: Run Tests
- Copy test inputs from above
- Paste into chat
- Compare actual vs expected results
- Mark status: ✅ Pass / ❌ Fail / ⚠️ Partial

### Step 5: Report Issues
If any test fails, note:
- Test ID
- Input used
- Expected result
- Actual result
- Screenshot (if helpful)

---

## 🐛 Known Limitations

1. **LLM Dependency**: Response quality depends on DeepSeek following instructions
2. **Hinglish Quality**: May vary based on model's training
3. **Ambiguous Questions**: Model may answer directly instead of asking for clarification
4. **Complex Queries**: Long questions might get partial answers

---

## 📊 Success Criteria

### Minimum Viable:
- ✅ 90% FAQ questions answered correctly
- ✅ 95% off-topic questions redirected
- ✅ 100% product data accurate (₹7L, fees, etc.)

### Excellent:
- ✅ 95% FAQ accuracy
- ✅ 80% Hinglish responses natural
- ✅ 90% unsupported languages detected

---

## 🚀 Quick Test Commands

**Check if app is running:**
```bash
./status.sh
```

**View live logs:**
```bash
tail -f logs/app.log
```

**Restart if needed:**
```bash
./stop.sh && sleep 2 && ./start.sh
```

---

*Ready to test! 🎉*
