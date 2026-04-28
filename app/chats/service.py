from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.db.models import Chat, Message, User
from app.llm.service import ask_llm


def list_chats(db: Session, user: User) -> list[Chat]:
    return (
        db.query(Chat)
        .filter(Chat.owner_id == user.id)
        .order_by(Chat.created_at.desc())
        .all()
    )


def create_chat(db: Session, user: User, title: str) -> Chat:
    chat = Chat(title=title or "new chat", owner_id=user.id)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_chat(db: Session, user: User, chat_id: int) -> Chat:
    chat = (
        db.query(Chat)
        .options(selectinload(Chat.messages))
        .filter(Chat.id == chat_id, Chat.owner_id == user.id)
        .first()
    )
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="chat not found")
    return chat


def add_message_and_answer(db: Session, user: User, chat_id: int, content: str) -> list[Message]:
    chat = get_chat(db, user, chat_id)

    user_message = Message(chat_id=chat.id, role="user", content=content)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    answer = ask_llm(content)
    assistant_message = Message(chat_id=chat.id, role="assistant", content=answer)
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return [user_message, assistant_message]


def save_streamed_exchange(db: Session, user: User, chat_id: int, user_content: str, assistant_content: str) -> None:
    chat = get_chat(db, user, chat_id)
    db.add(Message(chat_id=chat.id, role="user", content=user_content))
    db.add(Message(chat_id=chat.id, role="assistant", content=assistant_content))
    db.commit()
