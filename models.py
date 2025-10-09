from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime
from database import Base
import datetime
 
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    role = Column(String(50))
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), default=lambda : datetime.datetime.now(datetime.timezone.utc))