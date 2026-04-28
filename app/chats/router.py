from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.chats.service import add_message_and_answer, create_chat, get_chat, list_chats, save_streamed_exchange
from app.db.models import User
from app.db.session import get_db
from app.llm.service import stream_llm
from app.schemas.chat import ChatCreate, ChatDetail, ChatOut, MessageCreate, MessageOut

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("", response_model=list[ChatOut])
def chats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_chats(db, user)


@router.post("", response_model=ChatOut)
def new_chat(payload: ChatCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return create_chat(db, user, payload.title)


@router.get("/{chat_id}", response_model=ChatDetail)
def chat_detail(chat_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_chat(db, user, chat_id)


@router.post("/{chat_id}/messages", response_model=list[MessageOut])
def send_message(
    chat_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return add_message_and_answer(db, user, chat_id, payload.content)


@router.post("/{chat_id}/messages/stream")
def send_message_stream(
    chat_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    def generator():
        chunks: list[str] = []
        for token in stream_llm(payload.content):
            chunks.append(token)
            yield token
        save_streamed_exchange(db, user, chat_id, payload.content, "".join(chunks).strip())

    return StreamingResponse(generator(), media_type="text/plain")
