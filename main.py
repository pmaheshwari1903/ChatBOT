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

# ----- ENVIRONMENT SETUP -----
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("❌ GEMINI_API_KEY environment variable is missing")

print("✅ Loaded Gemini API key:", api_key[:4] + "****")

client = genai.Client(api_key=api_key)

# ----- FASTAPI APP -----
app = FastAPI()

# Create database tables if not exist
models.Base.metadata.create_all(bind=engine)

# ----- CORS SETUP -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ----- FRONTEND SETUP -----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")

@app.get("/", include_in_schema=False)
def serve_index():
    """Serve your single index.html file with inline CSS and JS."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        return {"error": "index.html not found"}
    return FileResponse(index_path)


# ----- SCHEMAS -----
class ChatResponse(BaseModel):
    message: str
    session_id: str


# ----- DATABASE SESSION -----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----- API ROUTES -----
@app.post("/chat")
def chat(req: ChatResponse, db: Session = Depends(get_db)):
    """Handles chat requests between user and Gemini model."""
    user_msg = ChatMessage(session_id=req.session_id, role="user", content=req.message)
    db.add(user_msg)
    db.commit()

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[req.message],
        )
        reply = response.text
        print(f"✅ Gemini response OK (session={req.session_id})")

    except Exception as e:
        print("❌ Gemini API Error:")
        import traceback
        traceback.print_exc()
        print("Error details:", str(e))
        reply = "Sorry, something went wrong while contacting the AI. Please try again later."

    bot_msg = ChatMessage(session_id=req.session_id, role="assistant", content=reply)
    db.add(bot_msg)
    db.commit()

    return {"reply": reply}


@app.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    """Return chat history for a given session."""
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    return [
        {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
        for msg in messages
    ]