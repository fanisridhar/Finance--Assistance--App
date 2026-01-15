from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import ChatMessage, ChatResponse
from app.services.security import get_current_user
from app.services.langchain_agent import FinanceAgent

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with the finance agent"""
    agent = FinanceAgent(db, current_user)
    response = agent.chat(message.message)
    
    return ChatResponse(
        response=response,
        conversation_id=message.conversation_id or "default",
        suggestions=None
    )

