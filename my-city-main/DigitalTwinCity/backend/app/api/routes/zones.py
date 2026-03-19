from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.simulation_history import SimulationHistory
from app.models.zone import Zone
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.schemas.zone import ZoneMetrics, ZoneResponse
from app.services.simulation_engine import SimulationEngine
from app.utils.helpers import dumps_json, loads_json

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("", response_model=list[ZoneResponse])
def get_zones(db: Session = Depends(get_db)) -> list[Zone]:
    return db.query(Zone).order_by(Zone.id.asc()).all()


@router.get("/{zone_id}", response_model=ZoneResponse)
def get_zone(zone_id: int, db: Session = Depends(get_db)) -> Zone:
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.post("/{zone_id}/simulate", response_model=SimulationResponse)
def simulate_zone_change(
    zone_id: int,
    payload: SimulationRequest,
    db: Session = Depends(get_db),
) -> SimulationResponse:
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    engine = SimulationEngine()
    try:
        simulation = engine.apply_to_zone(zone, payload.action_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    history = SimulationHistory(
        zone_id=zone.id,
        action_type=payload.action_type,
        note=payload.note,
        before_metrics=dumps_json(simulation["before_metrics"]),
        after_metrics=dumps_json(simulation["after_metrics"]),
        metric_impacts=dumps_json([impact.model_dump() for impact in simulation["metric_impacts"]]),
        before_urban_quality_index=simulation["before_urban_quality_index"],
        after_urban_quality_index=simulation["after_urban_quality_index"],
    )
    db.add(history)
    db.add(zone)
    db.commit()
    db.refresh(zone)
    db.refresh(history)

    return SimulationResponse(
        zone=zone,
        action_type=payload.action_type,
        note=payload.note,
        before_metrics=ZoneMetrics(**simulation["before_metrics"]),
        after_metrics=ZoneMetrics(**simulation["after_metrics"]),
        metric_impacts=simulation["metric_impacts"],
        before_urban_quality_index=simulation["before_urban_quality_index"],
        after_urban_quality_index=simulation["after_urban_quality_index"],
        created_at=history.created_at,
    )


@router.get("/{zone_id}/history")
def get_zone_history(zone_id: int, db: Session = Depends(get_db)) -> list[dict]:
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    history_items = (
        db.query(SimulationHistory)
        .filter(SimulationHistory.zone_id == zone_id)
        .order_by(SimulationHistory.created_at.desc())
        .all()
    )

    return [
        {
            "id": item.id,
            "zone_id": item.zone_id,
            "action_type": item.action_type,
            "note": item.note,
            "before_metrics": loads_json(item.before_metrics, default={}),
            "after_metrics": loads_json(item.after_metrics, default={}),
            "metric_impacts": loads_json(item.metric_impacts, default=[]),
            "before_urban_quality_index": item.before_urban_quality_index,
            "after_urban_quality_index": item.after_urban_quality_index,
            "created_at": item.created_at,
        }
        for item in history_items
    ]