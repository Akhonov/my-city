from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.suggestion import Suggestion
from app.schemas.analytics import BenefitAnalyticsResponse, DemandAnalyticsResponse
from app.services.ai_benefit_service import AIBenefitService
from app.utils.helpers import round2

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/demand", response_model=DemandAnalyticsResponse)
def get_demand_analytics(db: Session = Depends(get_db)) -> DemandAnalyticsResponse:
    suggestions = db.query(Suggestion).all()

    improvement_counts: dict[str, int] = defaultdict(int)
    zone_counts: dict[int, int] = defaultdict(int)
    hotspot_count = 0

    for suggestion in suggestions:
        improvement_counts[suggestion.improvement_type] += 1
        zone_counts[suggestion.zone_id] += 1
        if suggestion.is_hotspot:
            hotspot_count += 1

    totals_by_improvement = [
        {"improvement_type": improvement_type, "count": count}
        for improvement_type, count in sorted(
            improvement_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    totals_by_zone = [
        {"zone_id": zone_id, "count": count}
        for zone_id, count in sorted(zone_counts.items(), key=lambda item: item[1], reverse=True)
    ]

    return DemandAnalyticsResponse(
        totals_by_improvement=totals_by_improvement,
        totals_by_zone=totals_by_zone,
        hotspot_suggestions_count=hotspot_count,
        total_suggestions=len(suggestions),
    )


@router.get("/benefit", response_model=BenefitAnalyticsResponse)
def get_benefit_analytics(db: Session = Depends(get_db)) -> BenefitAnalyticsResponse:
    suggestions = db.query(Suggestion).all()

    benefit_scores: dict[str, list[float]] = defaultdict(list)
    priority_scores: dict[str, list[float]] = defaultdict(list)
    beneficial_flags: dict[str, list[int]] = defaultdict(list)
    zone_need_scores: dict[str, list[float]] = defaultdict(list)

    ai_service = AIBenefitService()

    for suggestion in suggestions:
        benefit_scores[suggestion.improvement_type].append(suggestion.benefit_score)
        priority_scores[suggestion.improvement_type].append(suggestion.priority_score)
        beneficial_flags[suggestion.improvement_type].append(1 if suggestion.beneficial else 0)

    for improvement_type in benefit_scores.keys():
        related = (
            db.query(Suggestion)
            .filter(Suggestion.improvement_type == improvement_type)
            .all()
        )
        for item in related:
            zone = item.zone_id
            if zone is None:
                continue

        items = (
            db.query(Suggestion)
            .filter(Suggestion.improvement_type == improvement_type)
            .all()
        )
        if items:
            inferred_need = []
            for item in items:
                inferred_need.append(round2((item.priority_score * 0.45) + (item.benefit_score * 0.55)))
            zone_need_scores[improvement_type].extend(inferred_need)

    average_benefit_score_by_improvement = [
        {
            "improvement_type": improvement_type,
            "average_benefit_score": round2(sum(values) / len(values)),
        }
        for improvement_type, values in benefit_scores.items()
        if values
    ]

    average_priority_score_by_improvement = [
        {
            "improvement_type": improvement_type,
            "average_priority_score": round2(sum(values) / len(values)),
        }
        for improvement_type, values in priority_scores.items()
        if values
    ]

    beneficial_share_by_improvement = [
        {
            "improvement_type": improvement_type,
            "beneficial_share_percent": round2((sum(values) / len(values)) * 100.0),
        }
        for improvement_type, values in beneficial_flags.items()
        if values
    ]

    average_zone_need_score_by_improvement = [
        {
            "improvement_type": improvement_type,
            "average_zone_need_score": round2(sum(values) / len(values)),
        }
        for improvement_type, values in zone_need_scores.items()
        if values
    ]

    average_benefit_score_by_improvement.sort(key=lambda item: item["average_benefit_score"], reverse=True)
    average_priority_score_by_improvement.sort(key=lambda item: item["average_priority_score"], reverse=True)
    beneficial_share_by_improvement.sort(key=lambda item: item["beneficial_share_percent"], reverse=True)
    average_zone_need_score_by_improvement.sort(key=lambda item: item["average_zone_need_score"], reverse=True)

    return BenefitAnalyticsResponse(
        average_benefit_score_by_improvement=average_benefit_score_by_improvement,
        average_priority_score_by_improvement=average_priority_score_by_improvement,
        beneficial_share_by_improvement=beneficial_share_by_improvement,
        average_zone_need_score_by_improvement=average_zone_need_score_by_improvement,
    )