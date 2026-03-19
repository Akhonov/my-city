from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.suggestion import Suggestion
from app.models.zone import Zone
from app.schemas.recommendation import HotspotRegion, RecommendationResponse
from app.services.recommendation_service import RecommendationService
from app.services.scoring_service import ScoringService
from app.utils.helpers import round2

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(db: Session = Depends(get_db)) -> RecommendationResponse:
    service = RecommendationService()
    return service.get_city_recommendations(db=db)


@router.get("/hotspots", response_model=list[HotspotRegion])
def get_hotspots(db: Session = Depends(get_db)) -> list[HotspotRegion]:
    suggestions = db.query(Suggestion).order_by(Suggestion.created_at.desc()).all()
    zones = {zone.id: zone for zone in db.query(Zone).all()}
    scoring_service = ScoringService()

    grouped: dict[tuple[int, str], list[Suggestion]] = defaultdict(list)
    for suggestion in suggestions:
        grouped[(suggestion.zone_id, suggestion.improvement_type)].append(suggestion)

    hotspots: list[HotspotRegion] = []
    for (zone_id, improvement_type), items in grouped.items():
        zone = zones.get(zone_id)
        if not zone:
            continue

        unique_users = {item.user_identifier for item in items}
        avg_lat = sum(item.latitude for item in items) / len(items)
        avg_lon = sum(item.longitude for item in items) / len(items)
        hotspot_score = round2(min((len(items) * 12) + (len(unique_users) * 10), 100.0))

        hotspots.append(
            HotspotRegion(
                improvement_type=improvement_type,
                zone_id=zone_id,
                zone_name=zone.name,
                center_latitude=avg_lat,
                center_longitude=avg_lon,
                suggestion_count=len(items),
                unique_users_count=len(unique_users),
                hotspot_score=hotspot_score,
                priority_level=scoring_service.score_to_priority_level(hotspot_score),
            )
        )

    return sorted(hotspots, key=lambda item: item.hotspot_score, reverse=True)