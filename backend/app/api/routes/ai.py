from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas import AIChatRequest, ParseTripRequest
from app.services.ai_service import chat_reply, parse_trip_text, save_conversation

router = APIRouter()


@router.post('/chat')
def chat(
    payload: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = chat_reply(payload.message)
    save_conversation(db, current_user.id, payload.message, result['reply'], result['parsed_intent'])
    return {
        'message': payload.message,
        'response': result['reply'],
        'parsed_intent': result['parsed_intent'],
    }


@router.post('/parse-trip')
def parse_trip(payload: ParseTripRequest) -> dict:
    return parse_trip_text(payload.text)
