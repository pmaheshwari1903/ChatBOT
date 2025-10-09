import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google import genai

import models
from models import ChatMessage
from database import engine, SessionLocal

# ----- Load ENV -----
load_dotenv()

if "GEMINI_API_KEY" not in os.environ:
    raise RuntimeError("❌ Please set GEMINI_API_KEY environment variable")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ----- FastAPI app -----
app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# ----- CORS -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ----- Frontend setup -----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")

# ✅ Mount static files (JS, CSS, images)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ----- Schema -----
class ChatResponse(BaseModel):
    message: str
    session_id: str

# ----- DB Dependency -----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- Serve Frontend -----
@app.get("/", include_in_schema=False)
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        return {"error": "index.html not found"}
    return FileResponse(index_path)

# ----- Chat API -----
@app.post("/chat")
def chat(req: ChatResponse, db: Session = Depends(get_db)):
    user_msg = ChatMessage(session_id=req.session_id, role="user", content=req.message)
    db.add(user_msg)
    db.commit()

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[req.message],
        )
        reply = response.text
    except Exception as e:
        reply = f"Error: {e}"

    bot_msg = ChatMessage(session_id=req.session_id, role="assistant", content=reply)
    db.add(bot_msg)
    db.commit()

    return {"reply": reply}

# ----- Chat History -----
@app.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    return [
        {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
        for msg in messages
    ]
