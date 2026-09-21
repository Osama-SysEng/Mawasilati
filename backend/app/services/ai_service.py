import re
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import AIConversation

CITY_HINTS = ['المعادي', 'المهندسين', 'مدينة نصر', 'الجيزة', 'وسط البلد', 'العباسية', 'حلوان', 'الهرم']


def _extract_budget(text: str) -> float | None:
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:جنيه|ج|l.e|egp)', text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def _extract_time_hint(text: str) -> str:
    if any(keyword in text for keyword in ['دلوقتي', 'حالاً', 'الآن', 'الان', 'فوراً', 'فورا']):
        return 'now'
    return 'later'


def _extract_location_after_keyword(text: str, keywords: list[str]) -> str | None:
    lower = text
    for keyword in keywords:
        pattern = rf'{re.escape(keyword)}\s+(.+?)(?=\s+(?:ومن|و|وعندي|بميزانية|ميزانية|دلوقتي|حالاً|الآن|الان|فوراً|فورا|\.|,|$))'
        match = re.search(pattern, lower)
        if match:
            return match.group(1).strip()
    return None


def parse_trip_text(text: str) -> dict:
    cleaned = text.strip()
    origin = _extract_location_after_keyword(cleaned, ['من'])
    destination = _extract_location_after_keyword(cleaned, ['إلى', 'الى', 'ل', 'لل'])
    budget = _extract_budget(cleaned)
    time_hint = _extract_time_hint(cleaned)
    suggested = [hint for hint in CITY_HINTS if hint in cleaned]
    return {
        'raw_text': cleaned,
        'origin': origin,
        'destination': destination,
        'budget': budget,
        'time_hint': time_hint,
        'mentioned_locations': suggested,
        'parsed_at': datetime.now(timezone.utc).isoformat(),
    }


def chat_reply(message: str) -> dict:
    parsed = parse_trip_text(message)
    if parsed['origin'] and parsed['destination']:
        reply = f"تمام، فهمت إنك رايح من {parsed['origin']} لـ {parsed['destination']}."
        if parsed['budget'] is not None:
            reply += f" وميزانيتك حوالي {parsed['budget']} جنيه."
        reply += ' أقدر أطلعلك أفضل الاختيارات حالاً.'
    else:
        reply = 'ابعتلي منين وفين وميزانيتك لو تحب، وأنا أطلعلك خطة رحلة مناسبة باللهجة المصرية.'
    return {
        'reply': reply,
        'parsed_intent': parsed,
    }


def save_conversation(db: Session, user_id: str, message: str, response: str, parsed_intent: dict) -> None:
    conversation = AIConversation(
        id=str(uuid4()),
        user_id=user_id,
        message=message,
        response=response,
        parsed_intent=parsed_intent,
    )
    db.add(conversation)
    db.commit()
