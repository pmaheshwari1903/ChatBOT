import os
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google import genai

import models
from models import ChatMessage
from database import engine, SessionLocal

# ─────────────────────────────────────────────
#  ENVIRONMENT SETUP
# ─────────────────────────────────────────────
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("❌ GEMINI_API_KEY environment variable is missing")

client = genai.Client(api_key=api_key)

# ─────────────────────────────────────────────
#  FASTAPI APP CONFIG
# ─────────────────────────────────────────────
app = FastAPI()

# Auto-create database tables
models.Base.metadata.create_all(bind=engine)

# Allow all CORS origins (you can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  FRONTEND SERVING
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")

@app.get("/", include_in_schema=False)
def serve_index():
    """Serve single-page index.html"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        return {"error": "index.html not found"}
    return FileResponse(index_path)

# ─────────────────────────────────────────────
#  DATABASE SESSION DEPENDENCY
# ─────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─────────────────────────────────────────────
#  REQUEST SCHEMA
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str

# ─────────────────────────────────────────────
#  CHAT ROUTE
# ─────────────────────────────────────────────
# @app.post("/chat")
# def chat(req: ChatRequest, db: Session = Depends(get_db)):
#     """Handle chat request with Gemini"""
#     db.add(ChatMessage(session_id=req.session_id, role="user", content=req.message))
#     db.commit()

#     try:
#         # ✅ Correct model path for google-genai
#         response = client.models.generate_content(
#             model="gemini-1.5-flash",
#             contents=[req.message],
#         )
#         reply = response.text or "No response from Gemini."
#     except Exception as e:
#         print("❌ Gemini API Error:", e)
#         reply = "Sorry, something went wrong while contacting the AI. Please try again later."

#     db.add(ChatMessage(session_id=req.session_id, role="assistant", content=reply))
#     db.commit()

#     return {"reply": reply}


@app.get("/test-gemini")
def test_gemini():
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=["Say 'Hello from Gemini'!"]
        )
        return {"success": True, "reply": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─────────────────────────────────────────────
#  CHAT HISTORY
# ─────────────────────────────────────────────
@app.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    """Return chat history for given session"""
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    return [
        {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
        for msg in messages
    ]
