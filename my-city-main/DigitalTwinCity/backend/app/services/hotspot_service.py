from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.placed_improvement import PlacedImprovement
from app.models.suggestion import Suggestion
from app.schemas.suggestion import HotspotAnalysisResponse
from app.utils.constants import IMPROVEMENT_TYPE_TO_ACTION
from app.utils.geo import is_within_radius
from app.utils.helpers import clamp, round2


class HotspotService:
    def analyze_new_suggestion(
        self,
        db: Session,
        zone_id: int,
        latitude: float,
        longitude: float,
        improvement_type: str,
    ) -> HotspotAnalysisResponse:
        return self.analyze_cross_entity(
            db=db,
            zone_id=zone_id,
            latitude=latitude,
            longitude=longitude,
            improvement_type=improvement_type,
            include_suggestions=True,
            include_improvements=True,
        )

    def analyze_new_improvement(
        self,
        db: Session,
        zone_id: int | None,
        latitude: float,
        longitude: float,
        improvement_type: str,
    ) -> HotspotAnalysisResponse:
        return self.analyze_cross_entity(
            db=db,
            zone_id=zone_id,
            latitude=latitude,
            longitude=longitude,
            improvement_type=improvement_type,
            include_suggestions=True,
            include_improvements=True,
        )

    def analyze_cross_entity(
        self,
        db: Session,
        zone_id: int | None,
        latitude: float,
        longitude: float,
        improvement_type: str,
        include_suggestions: bool = True,
        include_improvements: bool = True,
        exclude_suggestion_id: int | None = None,
        exclude_improvement_id: int | None = None,
    ) -> HotspotAnalysisResponse:
        target_action = self._to_action(improvement_type)

        exact_zone_matches_count = 0
        nearby_similar_requests_count = 0
        nearby_users: set[str] = set()

        if include_suggestions:
            suggestions = db.query(Suggestion).all()
            for suggestion in suggestions:
                if exclude_suggestion_id is not None and suggestion.id == exclude_suggestion_id:
                    continue
                if self._to_action(suggestion.improvement_type) != target_action:
                    continue

                if zone_id is not None and suggestion.zone_id == zone_id:
                    exact_zone_matches_count += 1

                if is_within_radius(
                    latitude,
                    longitude,
                    suggestion.latitude,
                    suggestion.longitude,
                    settings.HOTSPOT_RADIUS_METERS,
                ):
                    nearby_similar_requests_count += 1
                    if suggestion.user_identifier:
                        nearby_users.add(suggestion.user_identifier)

        if include_improvements:
            improvements = db.query(PlacedImprovement).all()
            for improvement in improvements:
                if exclude_improvement_id is not None and improvement.id == exclude_improvement_id:
                    continue
                if self._to_action(improvement.improvement_type) != target_action:
                    continue

                if zone_id is not None and improvement.zone_id == zone_id:
                    exact_zone_matches_count += 1

                if is_within_radius(
                    latitude,
                    longitude,
                    improvement.latitude,
                    improvement.longitude,
                    settings.HOTSPOT_RADIUS_METERS,
                ):
                    nearby_similar_requests_count += 1
                    if improvement.user_identifier:
                        nearby_users.add(improvement.user_identifier)

        unique_users_nearby_count = len(nearby_users)

        hotspot_score = round2(
            clamp(
                (exact_zone_matches_count * 10)
                + (nearby_similar_requests_count * 7)
                + (unique_users_nearby_count * 10),
                0.0,
                100.0,
            )
        )

        is_hotspot = hotspot_score >= 55 or (
            nearby_similar_requests_count >= 3 and unique_users_nearby_count >= 2
        )

        return HotspotAnalysisResponse(
            exact_zone_matches_count=exact_zone_matches_count,
            nearby_similar_requests_count=nearby_similar_requests_count,
            unique_users_nearby_count=unique_users_nearby_count,
            hotspot_score=hotspot_score,
            is_hotspot=is_hotspot,
            radius_meters=round2(settings.HOTSPOT_RADIUS_METERS),
        )

    def _to_action(self, improvement_type: str) -> str:
        normalized = improvement_type.strip().lower()
        return IMPROVEMENT_TYPE_TO_ACTION.get(normalized, normalized)