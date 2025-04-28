from sqlalchemy.orm import Session
from app.models import Event
from app.database import get_db

def record_event(event_name: str, user_id: int = None, metadata: dict = None):
    db: Session = next(get_db())
    event = Event(
        event_name=event_name,
        user_id=user_id,
        event_metadata=metadata or {}
    )
    db.add(event)
    db.commit()

def mask_email(email: str) -> str:
    if not email or "@" not in email:
        return ""
    local, domain = email.split("@")
    if len(local) > 1:
        return local[0] + "***@" + domain
    return "***@" + domain