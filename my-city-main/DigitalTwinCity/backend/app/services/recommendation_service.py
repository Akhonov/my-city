from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.suggestion import Suggestion
from app.models.zone import Zone
from app.schemas.recommendation import HotspotRegion, RecommendationItem, RecommendationResponse
from app.services.ai_benefit_service import AIBenefitService
from app.services.scoring_service import ScoringService
from app.utils.constants import DEFAULT_ACTION_ORDER
from app.utils.helpers import round2


class RecommendationService:
    def __init__(self) -> None:
        self.ai_benefit_service = AIBenefitService()
        self.scoring_service = ScoringService()

    def get_city_recommendations(self, db: Session) -> RecommendationResponse:
        zones = db.query(Zone).all()
        suggestions = db.query(Suggestion).all()

        recommendation_items: list[RecommendationItem] = []
        for zone in zones:
            for action_type in DEFAULT_ACTION_ORDER:
                analysis = self.ai_benefit_service.analyze(zone=zone, action_type=action_type, local_demand_signal=0.0)
                estimated_priority = round2((analysis.benefit_score * 0.7) + (analysis.zone_need_score * 0.3))
                recommendation_items.append(
                    RecommendationItem(
                        zone_id=zone.id,
                        zone_name=zone.name,
                        zone_type=zone.zone_type,
                        action_type=action_type,
                        benefit_score=analysis.benefit_score,
                        confidence=analysis.confidence,
                        zone_need_score=analysis.zone_need_score,
                        estimated_priority_score=estimated_priority,
                        explanation=analysis.explanation,
                    )
                )

        top_recommendations = sorted(
            recommendation_items,
            key=lambda item: (item.estimated_priority_score, item.benefit_score, item.confidence),
            reverse=True,
        )[:15]

        hotspot_regions = self._build_hotspots(zones, suggestions)
        most_requested_improvements = self._most_requested_improvements(suggestions)

        return RecommendationResponse(
            top_recommendations=top_recommendations,
            top_hotspots=hotspot_regions[:10],
            most_requested_improvements=most_requested_improvements,
        )

    def _build_hotspots(self, zones: list[Zone], suggestions: list[Suggestion]) -> list[HotspotRegion]:
        zone_map = {zone.id: zone for zone in zones}
        grouped: dict[tuple[int, str], list[Suggestion]] = defaultdict(list)

        for suggestion in suggestions:
            grouped[(suggestion.zone_id, suggestion.improvement_type)].append(suggestion)

        hotspots: list[HotspotRegion] = []
        for (zone_id, improvement_type), items in grouped.items():
            zone = zone_map.get(zone_id)
            if not zone:
                continue

            center_latitude = sum(item.latitude for item in items) / len(items)
            center_longitude = sum(item.longitude for item in items) / len(items)
            unique_users = {item.user_identifier for item in items}
            hotspot_score = round2(min((len(items) * 12) + (len(unique_users) * 10), 100.0))
            priority_level = self.scoring_service.score_to_priority_level(hotspot_score)

            hotspots.append(
                HotspotRegion(
                    improvement_type=improvement_type,
                    zone_id=zone_id,
                    zone_name=zone.name,
                    center_latitude=round2(center_latitude),
                    center_longitude=round2(center_longitude),
                    suggestion_count=len(items),
                    unique_users_count=len(unique_users),
                    hotspot_score=hotspot_score,
                    priority_level=priority_level,
                )
            )

        return sorted(hotspots, key=lambda item: item.hotspot_score, reverse=True)

    def _most_requested_improvements(self, suggestions: list[Suggestion]) -> list[dict]:
        counts: dict[str, int] = defaultdict(int)
        for suggestion in suggestions:
            counts[suggestion.improvement_type] += 1

        result = [{"improvement_type": key, "count": value} for key, value in counts.items()]
        return sorted(result, key=lambda item: item["count"], reverse=True)