import os
import uuid
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class ChatRequest(BaseModel):
    user_message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    ai_reply: str
    grammar_correction: Optional[str] = None
    session_id: str

# --- In-memory Storage ---
# Structure: { session_id: [ {"role": "user", "parts": ["msg"]}, ... ] }
# We will limit to last 10 turns (20 messages)
conversations: Dict[str, List[Dict[str, str]]] = {}

# --- Gemini Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
model = None

if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        # listing available models to debug
        available_models = [m.name for m in genai.list_models()]
        print(f"Available models: {available_models}")
        
        target_model = 'models/gemini-1.5-flash'
        if 'models/gemini-1.5-flash' not in available_models:
             # Try to find a valid chat model
             for m in available_models:
                 if 'gemini' in m and 'flash' in m:
                     target_model = m
                     break
                 if 'gemini' in m and 'pro' in m:
                     target_model = m
                     break
        
        print(f"Selected model: {target_model}")
        model = genai.GenerativeModel(target_model)
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
else:
    print("WARNING: GOOGLE_API_KEY not found. Running in MOCK mode.")

SYSTEM_PROMPT = """
You are a friendly, encouraging English conversation partner. 
Your goal is to chat naturally with the user, ask follow-up questions, and help them improve.
Output your response in JSON format with two keys:
1. "ai_reply": Your conversational response. Keep it natural, somewhat concise (1-3 sentences), and supportive.
2. "grammar_correction": If the user made a grammar mistake, provide a gentle correction and brief explanation. If no mistake using standard English, return null or an empty string.

Example Interaction:
User: "I does goes to store yesterday."
Response: {
  "ai_reply": "Oh, you went to the store? What did you buy there?",
  "grammar_correction": "Better validation: 'I went to the store yesterday.' (Use past tense 'went' instead of 'does goes')."
}

User: "I love reading books."
Response: {
  "ai_reply": "That's great! What genre do you like the most?",
  "grammar_correction": null
}

Strictly adhere to this JSON structure.
"""

def manage_history(session_id: str, new_message: dict):
    if session_id not in conversations:
        conversations[session_id] = []
    
    conversations[session_id].append(new_message)
    
    # Keep only last 20 messages (10 turns)
    if len(conversations[session_id]) > 20:
        conversations[session_id] = conversations[session_id][-20:]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    user_text = request.user_message
    
    # Add user message to history
    manage_history(session_id, {"role": "user", "parts": [user_text]})

    ai_reply = ""
    grammar_correction = None

    if model:
        try:
            # Construct the chat session with history
            # Gemini python lib manages history, but for simplicity/control we might pass it raw
            # or just use start_chat with history.
            
            # Formatting history for Gemini: needs to be list of content objects or dicts
            # We already store it as valid schema roughly, but let's be precise.
            gemini_history = []
            # We intentionally exclude the current user message effectively because `start_chat` history 
            # is *past* history, and we `send_message` the new one.
            # However, we need to inject the system prompt. 
            # Gemini 1.5 allows system instructions in the model creation, but we instantiated it globally.
            # We will use a simple approach: Prepend system prompt to the call or use generation_config with response_mime_type "application/json"
            
            current_history = conversations[session_id][:-1] # details except latest
            
            # Simple stateless call with context included in prompt might be safer for format enforcement
            # But let's try the chat Interface.
            chat = model.start_chat(history=[])
            
            # Forcing JSON mode using prompt engineering mostly, 
            # passing the context manually.
            
            context_str = "\\n".join([f"{msg['role'].upper()}: {msg['parts'][0]}" for msg in conversations[session_id]])
            
            full_prompt = f"{SYSTEM_PROMPT}\\n\\nConversation History:\\n{context_str}\\n\\nRespond in JSON:"
            
            response = model.generate_content(full_prompt, generation_config={"response_mime_type": "application/json"})
            import json
            data = json.loads(response.text)
            ai_reply = data.get("ai_reply", "I'm sorry, I didn't catch that.")
            grammar_correction = data.get("grammar_correction")

        except Exception as e:
            print(f"Error calling Gemini: {e}")
            ai_reply = f"I'm having trouble connecting to my brain right now. Error details: {str(e)}"
            grammar_correction = None
    else:
        # Mock Response
        ai_reply = f"I heard you say: '{user_text}'. (MockAI Mode - Set API Key to chat real!)"
        grammar_correction = None

    # Update history with AI response
    manage_history(session_id, {"role": "model", "parts": [ai_reply]})

    return ChatResponse(
        ai_reply=ai_reply,
        grammar_correction=grammar_correction,
        session_id=session_id
    )

# Mount the frontend directory to serve static files
from fastapi.staticfiles import StaticFiles
# Mount to root, so index.html is served at /
# We use absolute path or relative to main.py
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"WARNING: Frontend directory not found at {frontend_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
