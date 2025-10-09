import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, List, Annotated
from Backend.models import ChatMessage
import models
from Backend.database import engine,SessionLocal
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from google import genai


load_dotenv()

if "GEMINI_API_KEY" not in os.environ:
    raise RuntimeError("Please Give GEMINI_API_KEY environment variable")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)
        
# Schema:

class ChatResponse(BaseModel):
    message : str
    session_id : str
    
# Db Open and Close
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# root Check

@app.get("/")
def root():
    return {"message" : "ChatBot is running"}


@app.post("/chat")
def chat(req: ChatResponse, db: Session = Depends(get_db)):
    user_msg = ChatMessage(session_id=req.session_id, role="user", content=req.message)
    db.add(user_msg)
    db.commit()
    
    
    # Gemini ko sawal pucha!
    try:
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[req.message],
    )
        reply = response.text
    except Exception as e:
        reply = f"Error : {e}"
        
        
    # gemini ka reply save krenge
    
    bot_msg = ChatMessage(session_id = req.session_id, role = "assistant", content = reply)
    db.add(bot_msg)
    db.commit()
    
    return {"reply" : reply}



@app.get("/history/{session_id}")
def get_history(session_id : str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    return [
        {
            "role" : msg.role,
            "content" : msg.content,
            "timestamp" : msg.timestamp
        }
        for msg in messages
    ]