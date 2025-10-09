import os
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import google.generativeai as genai

import models
from models import ChatMessage
from database import engine, SessionLocal

# ----- ENVIRONMENT SETUP -----
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("❌ GEMINI_API_KEY environment variable is missing")

print("✅ Loaded Gemini API key:", api_key[:4] + "****")

# Configure Gemini client
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# ----- FASTAPI APP -----
app = FastAPI()

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# ----- CORS -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ----- FRONTEND -----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")

@app.get("/", include_in_schema=False)
def serve_index():
    """Serve index.html"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        return {"error": "index.html not found"}
    return FileResponse(index_path)

# ----- SCHEMAS -----
class ChatRequest(BaseModel):
    message: str
    session_id: str

# ----- DATABASE -----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- TEST GEMINI -----
@app.get("/check-gemini")
def check_gemini():
    """Quick Gemini API test."""
    try:
        test_model = genai.GenerativeModel("gemini-1.5-flash")
        response = test_model.generate_content("Say 'Gemini API is working!'")
        return {"success": True, "reply": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ----- CHAT -----
@app.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Handles chat requests with Gemini model."""
    # Save user message
    db.add(ChatMessage(session_id=req.session_id, role="user", content=req.message))
    db.commit()

    try:
        response = model.generate_content(req.message)
        reply = response.text
        print(f"✅ Gemini response OK (session={req.session_id})")
    except Exception as e:
        print("❌ Gemini API Error:", e)
        reply = "Sorry, something went wrong while contacting the AI. Please try again later."

    # Save bot message
    db.add(ChatMessage(session_id=req.session_id, role="assistant", content=reply))
    db.commit()

    return {"reply": reply}

# ----- HISTORY -----
@app.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a session."""
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    return [
        {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
        for msg in messages
    ]
