from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.priority_alert import PriorityAlert
from app.models.suggestion import Suggestion
from app.models.zone import Zone
from app.schemas.suggestion import SuggestionCreate, SuggestionResponse
from app.services.ai_benefit_service import AIBenefitService
from app.services.hotspot_service import HotspotService
from app.services.scoring_service import ScoringService
from app.services.telegram_service import TelegramService
from app.utils.helpers import dumps_json, round2


class SuggestionAnalysisService:
    def __init__(self) -> None:
        self.ai_benefit_service = AIBenefitService()
        self.hotspot_service = HotspotService()
        self.scoring_service = ScoringService()
        self.telegram_service = TelegramService()

    def analyze_and_save(self, db: Session, payload: SuggestionCreate) -> SuggestionResponse:
        zone = db.query(Zone).filter(Zone.id == payload.zone_id).first()
        if not zone:
            raise ValueError(f"Zone with id={payload.zone_id} not found")

        hotspot_analysis = self.hotspot_service.analyze_new_suggestion(
            db=db,
            zone_id=payload.zone_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            improvement_type=payload.improvement_type,
        )

        local_demand_signal = (
            (hotspot_analysis.exact_zone_matches_count * 10)
            + (hotspot_analysis.nearby_similar_requests_count * 6)
            + (hotspot_analysis.unique_users_nearby_count * 8)
        )

        benefit_analysis = self.ai_benefit_service.analyze(
            zone=zone,
            action_type=payload.improvement_type,
            local_demand_signal=local_demand_signal,
        )

        priority_score = self._calculate_priority_score(
            benefit_score=benefit_analysis.benefit_score,
            zone_need_score=benefit_analysis.zone_need_score,
            exact_zone_matches_count=hotspot_analysis.exact_zone_matches_count,
            nearby_similar_requests_count=hotspot_analysis.nearby_similar_requests_count,
            unique_users_nearby_count=hotspot_analysis.unique_users_nearby_count,
            hotspot_score=hotspot_analysis.hotspot_score,
        )
        priority_level = self.scoring_service.score_to_priority_level(priority_score)

        suggestion = Suggestion(
            zone_id=payload.zone_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            improvement_type=payload.improvement_type,
            note=payload.note,
            user_identifier=payload.user_identifier,
            benefit_score=benefit_analysis.benefit_score,
            confidence=benefit_analysis.confidence,
            priority_score=priority_score,
            priority_level=priority_level,
            beneficial=benefit_analysis.beneficial,
            exact_zone_matches_count=hotspot_analysis.exact_zone_matches_count,
            nearby_similar_requests_count=hotspot_analysis.nearby_similar_requests_count,
            unique_users_nearby_count=hotspot_analysis.unique_users_nearby_count,
            hotspot_score=hotspot_analysis.hotspot_score,
            is_hotspot=hotspot_analysis.is_hotspot,
            explanation=benefit_analysis.explanation,
            tradeoffs=dumps_json(benefit_analysis.tradeoffs),
            metric_impacts=dumps_json([impact.model_dump() for impact in benefit_analysis.metric_impacts]),
            telegram_triggered=False,
        )
        db.add(suggestion)
        db.commit()
        db.refresh(suggestion)

        alert_created = False
        telegram_triggered = False

        if priority_score >= settings.PRIORITY_ALERT_THRESHOLD:
            alert = self._create_alert(
                db=db,
                zone=zone,
                suggestion=suggestion,
                benefit_analysis=benefit_analysis,
                hotspot_analysis=hotspot_analysis,
                priority_score=priority_score,
                priority_level=priority_level,
            )
            alert_created = True
            telegram_triggered = self.telegram_service.send_priority_alert(db=db, alert=alert, zone=zone)
            if telegram_triggered:
                suggestion.telegram_triggered = True
                alert.telegram_sent = True
                db.add(suggestion)
                db.add(alert)
                db.commit()

        db.refresh(suggestion)

        return SuggestionResponse(
            suggestion=suggestion,
            benefit_analysis=benefit_analysis,
            hotspot_analysis=hotspot_analysis,
            priority_score=round2(priority_score),
            priority_level=priority_level,
            alert_created=alert_created,
            telegram_triggered=telegram_triggered,
        )

    def _calculate_priority_score(
        self,
        benefit_score: float,
        zone_need_score: float,
        exact_zone_matches_count: int,
        nearby_similar_requests_count: int,
        unique_users_nearby_count: int,
        hotspot_score: float,
    ) -> float:
        exact_zone_signal = min(exact_zone_matches_count * 18, 100)
        nearby_signal = min(nearby_similar_requests_count * 14, 100)
        uniqueness_signal = min(unique_users_nearby_count * 20, 100)

        score = (
            0.35 * benefit_score
            + 0.18 * exact_zone_signal
            + 0.16 * nearby_signal
            + 0.16 * zone_need_score
            + 0.08 * uniqueness_signal
            + 0.07 * hotspot_score
        )
        return round2(min(score, 100.0))

    def _create_alert(
        self,
        db: Session,
        zone: Zone,
        suggestion: Suggestion,
        benefit_analysis,
        hotspot_analysis,
        priority_score: float,
        priority_level: str,
    ) -> PriorityAlert:
        alert = PriorityAlert(
            zone_id=zone.id,
            improvement_type=suggestion.improvement_type,
            latitude=suggestion.latitude,
            longitude=suggestion.longitude,
            priority_score=priority_score,
            priority_level=priority_level,
            exact_zone_matches_count=hotspot_analysis.exact_zone_matches_count,
            nearby_similar_requests_count=hotspot_analysis.nearby_similar_requests_count,
            unique_users_nearby_count=hotspot_analysis.unique_users_nearby_count,
            hotspot_score=hotspot_analysis.hotspot_score,
            ai_beneficial=benefit_analysis.beneficial,
            ai_benefit_score=benefit_analysis.benefit_score,
            ai_confidence=benefit_analysis.confidence,
            summary=benefit_analysis.explanation,
            recommended_action=self._recommended_action(priority_level, suggestion.improvement_type),
            telegram_sent=False,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    def _recommended_action(self, priority_level: str, improvement_type: str) -> str:
        label = improvement_type.replace("_", " ")
        if priority_level == "critical":
            return f"Escalate for rapid city review and field validation of {label}."
        if priority_level == "high":
            return f"Queue for near-term planning review and feasibility assessment of {label}."
        if priority_level == "medium":
            return f"Keep under monitoring and compare with competing interventions for {label}."
        return f"Record demand and re-evaluate later for {label}."