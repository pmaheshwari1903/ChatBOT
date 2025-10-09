import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from models import ChatMessage
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from google import genai

# Load environment variables
load_dotenv()

if "GEMINI_API_KEY" not in os.environ:
    raise RuntimeError("Please set GEMINI_API_KEY environment variable")

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Create FastAPI app
app = FastAPI()

# Database setup
models.Base.metadata.create_all(bind=engine)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Define Frontend directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")

# Pydantic schema
class ChatResponse(BaseModel):
    message: str
    session_id: str

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Serve frontend index.html
@app.get("/", include_in_schema=False)
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        return {"error": "index.html not found"}
    return FileResponse(index_path)

# Chat endpoint
@app.post("/chat")
def chat(req: ChatResponse, db: Session = Depends(get_db)):
    # Save user message
    user_msg = ChatMessage(session_id=req.session_id, role="user", content=req.message)
    db.add(user_msg)
    db.commit()

    # Query Gemini model
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[req.message],
        )
        reply = response.text
    except Exception as e:
        reply = f"Error: {e}"

    # Save bot reply
    bot_msg = ChatMessage(session_id=req.session_id, role="assistant", content=reply)
    db.add(bot_msg)
    db.commit()

    return {"reply": reply}

# Chat history endpoint
@app.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp
        }
        for msg in messages
    ]
