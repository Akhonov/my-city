from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse

router = APIRouter(tags=["chat"])


@router.get("/messages", response_model=list[ChatMessageResponse], summary="Get chat messages")
def get_messages(db: Session = Depends(get_db)) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .limit(100)
        .all()
    )


@router.post("/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED, summary="Send chat message")
def create_message(payload: ChatMessageCreate, db: Session = Depends(get_db)) -> ChatMessage:
    message = ChatMessage(sender=payload.sender.strip(), text=payload.text.strip())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
