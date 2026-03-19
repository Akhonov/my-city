from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.suggestion import Suggestion
from app.schemas.suggestion import SuggestionCreate, SuggestionListItem, SuggestionResponse
from app.services.suggestion_analysis_service import SuggestionAnalysisService
from app.utils.helpers import loads_json

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.post("", response_model=SuggestionResponse)
def create_suggestion(
    payload: SuggestionCreate,
    db: Session = Depends(get_db),
) -> SuggestionResponse:
    service = SuggestionAnalysisService()
    try:
        return service.analyze_and_save(db=db, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[SuggestionListItem])
def get_suggestions(db: Session = Depends(get_db)) -> list[Suggestion]:
    return db.query(Suggestion).order_by(Suggestion.created_at.desc()).all()


@router.get("/{suggestion_id}")
def get_suggestion(suggestion_id: int, db: Session = Depends(get_db)) -> dict:
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    return {
        "id": suggestion.id,
        "zone_id": suggestion.zone_id,
        "latitude": suggestion.latitude,
        "longitude": suggestion.longitude,
        "improvement_type": suggestion.improvement_type,
        "note": suggestion.note,
        "user_identifier": suggestion.user_identifier,
        "benefit_score": suggestion.benefit_score,
        "confidence": suggestion.confidence,
        "priority_score": suggestion.priority_score,
        "priority_level": suggestion.priority_level,
        "beneficial": suggestion.beneficial,
        "exact_zone_matches_count": suggestion.exact_zone_matches_count,
        "nearby_similar_requests_count": suggestion.nearby_similar_requests_count,
        "unique_users_nearby_count": suggestion.unique_users_nearby_count,
        "hotspot_score": suggestion.hotspot_score,
        "is_hotspot": suggestion.is_hotspot,
        "explanation": suggestion.explanation,
        "tradeoffs": loads_json(suggestion.tradeoffs, default=[]),
        "metric_impacts": loads_json(suggestion.metric_impacts, default=[]),
        "telegram_triggered": suggestion.telegram_triggered,
        "created_at": suggestion.created_at,
    }