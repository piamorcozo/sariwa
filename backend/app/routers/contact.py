from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ContactMessage
from ..schemas import ContactIn, ContactOut

router = APIRouter(prefix="/api/contact", tags=["contact"])


@router.post("", response_model=ContactOut)
def send_message(payload: ContactIn, db: Session = Depends(get_db)):
    db.add(
        ContactMessage(
            name=payload.name.strip(),
            email=str(payload.email).lower(),
            phone=payload.phone,
            topic=payload.topic,
            message=payload.message.strip(),
        )
    )
    db.commit()
    return ContactOut(ok=True, message="Thanks — we'll reply within one business day.")
