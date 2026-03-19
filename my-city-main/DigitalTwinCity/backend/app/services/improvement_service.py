from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.placed_improvement import PlacedImprovement
from app.models.priority_alert import PriorityAlert
from app.models.simulation_history import SimulationHistory
from app.models.zone import Zone
from app.schemas.improvement import (
    ImprovementApplyResponse,
    ImprovementCreateResponse,
    PlacedImprovementCreate,
)
from app.services.ai_benefit_service import AIBenefitService
from app.services.geojson_service import GeoJSONService
from app.services.hotspot_service import HotspotService
from app.services.scoring_service import ScoringService
from app.services.simulation_engine import SimulationEngine
from app.services.telegram_service import TelegramService
from app.utils.constants import ACTION_TO_MAP_IMPROVEMENT_TYPE, IMPROVEMENT_TYPE_TO_ACTION
from app.utils.geo import haversine_distance_meters
from app.utils.helpers import dumps_json, loads_json, round2


class ImprovementService:
    def __init__(self) -> None:
        self.ai_benefit_service = AIBenefitService()
        self.hotspot_service = HotspotService()
        self.scoring_service = ScoringService()
        self.simulation_engine = SimulationEngine()
        self.telegram_service = TelegramService()
        self.geojson_service = GeoJSONService()

    def create_improvement(
        self,
        db: Session,
        payload: PlacedImprovementCreate,
    ) -> ImprovementCreateResponse:
        zone = self._resolve_zone(
            db=db,
            zone_id=payload.zone_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        if not zone:
            raise ValueError("Unable to resolve a target zone for this improvement")

        action_type = self._to_action(payload.improvement_type)
        improvement_type = self._to_map_improvement_type(action_type)

        hotspot_analysis = self.hotspot_service.analyze_new_improvement(
            db=db,
            zone_id=zone.id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            improvement_type=improvement_type,
        )

        local_demand_signal = (
            (hotspot_analysis.exact_zone_matches_count * 10)
            + (hotspot_analysis.nearby_similar_requests_count * 6)
            + (hotspot_analysis.unique_users_nearby_count * 8)
        )

        benefit_analysis = self.ai_benefit_service.analyze(
            zone=zone,
            action_type=action_type,
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

        improvement = PlacedImprovement(
            zone_id=zone.id,
            improvement_type=improvement_type,
            latitude=payload.latitude,
            longitude=payload.longitude,
            title=payload.title,
            description=payload.description,
            status="proposed",
            source=(payload.source or "user").strip().lower(),
            user_identifier=payload.user_identifier,
            ai_beneficial=benefit_analysis.beneficial,
            ai_benefit_score=benefit_analysis.benefit_score,
            ai_confidence=benefit_analysis.confidence,
            priority_score=priority_score,
            hotspot_score=hotspot_analysis.hotspot_score,
            exact_zone_matches_count=hotspot_analysis.exact_zone_matches_count,
            nearby_similar_requests_count=hotspot_analysis.nearby_similar_requests_count,
            unique_users_nearby_count=hotspot_analysis.unique_users_nearby_count,
            explanation=benefit_analysis.explanation,
            tradeoffs=dumps_json(benefit_analysis.tradeoffs),
            metric_impacts=dumps_json([impact.model_dump() for impact in benefit_analysis.metric_impacts]),
            metadata_json=dumps_json(payload.metadata_json) if payload.metadata_json is not None else None,
            geometry_type="Point",
        )

        db.add(improvement)
        db.commit()
        db.refresh(improvement)

        auto_applied = False
        telegram_triggered = False

        if payload.auto_apply and benefit_analysis.beneficial and benefit_analysis.benefit_score >= 65:
            self.apply_improvement(db=db, improvement_id=improvement.id)
            db.refresh(improvement)
            auto_applied = True

        if priority_score >= settings.PRIORITY_ALERT_THRESHOLD:
            alert = self._create_alert(
                db=db,
                zone=zone,
                improvement=improvement,
                benefit_analysis=benefit_analysis,
                hotspot_analysis=hotspot_analysis,
                priority_score=priority_score,
                priority_level=priority_level,
            )
            telegram_triggered = self.telegram_service.send_priority_alert(
                db=db,
                alert=alert,
                zone=zone,
            )
            if telegram_triggered:
                alert.telegram_sent = True
                db.add(alert)
                db.commit()

        db.refresh(improvement)

        return ImprovementCreateResponse(
            placed_improvement=improvement,
            benefit_analysis=benefit_analysis,
            hotspot_analysis=hotspot_analysis,
            priority_score=round2(priority_score),
            priority_level=priority_level,
            auto_applied=auto_applied,
            telegram_triggered=telegram_triggered,
        )

    def list_improvements(
        self,
        db: Session,
        zone_id: int | None = None,
        improvement_type: str | None = None,
        status: str | None = None,
        source: str | None = None,
    ) -> list[PlacedImprovement]:
        query = db.query(PlacedImprovement)

        if zone_id is not None:
            query = query.filter(PlacedImprovement.zone_id == zone_id)

        if improvement_type:
            normalized_action = self._to_action(improvement_type)
            normalized_type = self._to_map_improvement_type(normalized_action)
            query = query.filter(PlacedImprovement.improvement_type == normalized_type)

        if status:
            query = query.filter(PlacedImprovement.status == status.strip().lower())

        if source:
            query = query.filter(PlacedImprovement.source == source.strip().lower())

        return query.order_by(PlacedImprovement.created_at.desc()).all()

    def get_improvement(self, db: Session, improvement_id: int) -> PlacedImprovement | None:
        return db.query(PlacedImprovement).filter(PlacedImprovement.id == improvement_id).first()

    def get_improvement_detail(self, db: Session, improvement_id: int) -> dict | None:
        improvement = self.get_improvement(db=db, improvement_id=improvement_id)
        if not improvement:
            return None

        return {
            "id": improvement.id,
            "zone_id": improvement.zone_id,
            "improvement_type": improvement.improvement_type,
            "latitude": improvement.latitude,
            "longitude": improvement.longitude,
            "title": improvement.title,
            "description": improvement.description,
            "status": improvement.status,
            "source": improvement.source,
            "user_identifier": improvement.user_identifier,
            "ai_beneficial": improvement.ai_beneficial,
            "ai_benefit_score": improvement.ai_benefit_score,
            "ai_confidence": improvement.ai_confidence,
            "priority_score": improvement.priority_score,
            "hotspot_score": improvement.hotspot_score,
            "exact_zone_matches_count": improvement.exact_zone_matches_count,
            "nearby_similar_requests_count": improvement.nearby_similar_requests_count,
            "unique_users_nearby_count": improvement.unique_users_nearby_count,
            "explanation": improvement.explanation,
            "tradeoffs": loads_json(improvement.tradeoffs, default=[]),
            "metric_impacts": loads_json(improvement.metric_impacts, default=[]),
            "metadata_json": loads_json(improvement.metadata_json, default=None) if improvement.metadata_json else None,
            "geometry_type": improvement.geometry_type,
            "created_at": improvement.created_at,
            "updated_at": improvement.updated_at,
        }

    def update_status(
        self,
        db: Session,
        improvement_id: int,
        status: str,
    ) -> PlacedImprovement:
        improvement = self.get_improvement(db=db, improvement_id=improvement_id)
        if not improvement:
            raise ValueError(f"Improvement with id={improvement_id} not found")

        normalized_status = status.strip().lower()
        allowed_statuses = {"proposed", "approved", "applied", "rejected"}
        if normalized_status not in allowed_statuses:
            raise ValueError(f"Unsupported status: {status}")

        if normalized_status == "applied" and improvement.status != "applied":
            self.apply_improvement(db=db, improvement_id=improvement_id)
            improvement = self.get_improvement(db=db, improvement_id=improvement_id)
            if not improvement:
                raise ValueError(f"Improvement with id={improvement_id} not found after apply")
            return improvement

        improvement.status = normalized_status
        db.add(improvement)
        db.commit()
        db.refresh(improvement)
        return improvement

    def apply_improvement(
        self,
        db: Session,
        improvement_id: int,
    ) -> ImprovementApplyResponse:
        improvement = self.get_improvement(db=db, improvement_id=improvement_id)
        if not improvement:
            raise ValueError(f"Improvement with id={improvement_id} not found")

        if improvement.zone_id is None:
            raise ValueError("Improvement is not linked to a zone and cannot be applied")

        if improvement.status == "applied":
            raise ValueError("Improvement is already applied")

        zone = db.query(Zone).filter(Zone.id == improvement.zone_id).first()
        if not zone:
            raise ValueError("Linked zone not found")

        action_type = self._to_action(improvement.improvement_type)
        simulation = self.simulation_engine.apply_to_zone(zone, action_type)

        history = SimulationHistory(
            zone_id=zone.id,
            action_type=action_type,
            note=f"Applied from placed improvement #{improvement.id}",
            before_metrics=dumps_json(simulation["before_metrics"]),
            after_metrics=dumps_json(simulation["after_metrics"]),
            metric_impacts=dumps_json([impact.model_dump() for impact in simulation["metric_impacts"]]),
            before_urban_quality_index=simulation["before_urban_quality_index"],
            after_urban_quality_index=simulation["after_urban_quality_index"],
        )

        improvement.status = "applied"

        db.add(zone)
        db.add(history)
        db.add(improvement)
        db.commit()
        db.refresh(improvement)

        return ImprovementApplyResponse(
            placed_improvement=improvement,
            before_metrics=simulation["before_metrics"],
            after_metrics=simulation["after_metrics"],
            metric_impacts=simulation["metric_impacts"],
            before_urban_quality_index=simulation["before_urban_quality_index"],
            after_urban_quality_index=simulation["after_urban_quality_index"],
            status="applied",
        )

    def get_geojson(
        self,
        db: Session,
        zone_id: int | None = None,
        improvement_type: str | None = None,
        status: str | None = None,
        source: str | None = None,
    ):
        improvements = self.list_improvements(
            db=db,
            zone_id=zone_id,
            improvement_type=improvement_type,
            status=status,
            source=source,
        )
        return self.geojson_service.build_feature_collection(improvements)

    def get_hotspot_regions(self, db: Session):
        improvements = db.query(PlacedImprovement).order_by(PlacedImprovement.created_at.desc()).all()
        zones = db.query(Zone).all()
        return self.geojson_service.build_hotspot_regions(improvements, zones)

    def _resolve_zone(
        self,
        db: Session,
        zone_id: int | None,
        latitude: float,
        longitude: float,
    ) -> Zone | None:
        if zone_id is not None:
            return db.query(Zone).filter(Zone.id == zone_id).first()

        zones = db.query(Zone).all()
        if not zones:
            return None

        return min(
            zones,
            key=lambda zone: haversine_distance_meters(latitude, longitude, zone.latitude, zone.longitude),
        )

    def _to_action(self, improvement_type: str) -> str:
        normalized = improvement_type.strip().lower()
        action = IMPROVEMENT_TYPE_TO_ACTION.get(normalized)
        if not action:
            raise ValueError(f"Unsupported improvement_type: {improvement_type}")
        return action

    def _to_map_improvement_type(self, action_type: str) -> str:
        return ACTION_TO_MAP_IMPROVEMENT_TYPE.get(action_type, action_type)

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
        improvement: PlacedImprovement,
        benefit_analysis,
        hotspot_analysis,
        priority_score: float,
        priority_level: str,
    ) -> PriorityAlert:
        alert = PriorityAlert(
            zone_id=zone.id,
            improvement_type=improvement.improvement_type,
            latitude=improvement.latitude,
            longitude=improvement.longitude,
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
            recommended_action=self._recommended_action(priority_level, improvement.improvement_type),
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