from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.priority_alert import PriorityAlert
from app.schemas.alert import AlertResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
def get_alerts(db: Session = Depends(get_db)) -> list[PriorityAlert]:
    return db.query(PriorityAlert).order_by(PriorityAlert.created_at.desc()).all()