from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.improvement import (
    GeoJSONFeatureCollection,
    ImprovementApplyResponse,
    ImprovementCreateResponse,
    ImprovementHotspotRegion,
    PlacedImprovementCreate,
    PlacedImprovementDetailResponse,
    PlacedImprovementResponse,
    PlacedImprovementStatusUpdate,
)
from app.services.improvement_service import ImprovementService

router = APIRouter(prefix="/improvements", tags=["improvements"])


@router.post("", response_model=ImprovementCreateResponse)
def create_improvement(
    payload: PlacedImprovementCreate,
    db: Session = Depends(get_db),
) -> ImprovementCreateResponse:
    service = ImprovementService()
    try:
        return service.create_improvement(db=db, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[PlacedImprovementResponse])
def get_improvements(
    zone_id: int | None = Query(default=None),
    improvement_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    source: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list:
    service = ImprovementService()
    return service.list_improvements(
        db=db,
        zone_id=zone_id,
        improvement_type=improvement_type,
        status=status,
        source=source,
    )


@router.get("/geojson", response_model=GeoJSONFeatureCollection)
def get_improvements_geojson(
    zone_id: int | None = Query(default=None),
    improvement_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    source: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> GeoJSONFeatureCollection:
    service = ImprovementService()
    return service.get_geojson(
        db=db,
        zone_id=zone_id,
        improvement_type=improvement_type,
        status=status,
        source=source,
    )


@router.get("/hotspots", response_model=list[ImprovementHotspotRegion])
def get_improvement_hotspots(db: Session = Depends(get_db)) -> list[ImprovementHotspotRegion]:
    service = ImprovementService()
    return service.get_hotspot_regions(db=db)


@router.get("/by-zone/{zone_id}", response_model=list[PlacedImprovementResponse])
def get_improvements_by_zone(
    zone_id: int,
    db: Session = Depends(get_db),
) -> list:
    service = ImprovementService()
    return service.list_improvements(db=db, zone_id=zone_id)


@router.get("/{improvement_id}", response_model=PlacedImprovementDetailResponse)
def get_improvement(
    improvement_id: int,
    db: Session = Depends(get_db),
) -> PlacedImprovementDetailResponse:
    service = ImprovementService()
    improvement = service.get_improvement_detail(db=db, improvement_id=improvement_id)
    if not improvement:
        raise HTTPException(status_code=404, detail="Improvement not found")
    return PlacedImprovementDetailResponse(**improvement)


@router.patch("/{improvement_id}/status", response_model=PlacedImprovementResponse)
def update_improvement_status(
    improvement_id: int,
    payload: PlacedImprovementStatusUpdate,
    db: Session = Depends(get_db),
) -> PlacedImprovementResponse:
    service = ImprovementService()
    try:
        return service.update_status(db=db, improvement_id=improvement_id, status=payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{improvement_id}/apply", response_model=ImprovementApplyResponse)
def apply_improvement(
    improvement_id: int,
    db: Session = Depends(get_db),
) -> ImprovementApplyResponse:
    service = ImprovementService()
    try:
        return service.apply_improvement(db=db, improvement_id=improvement_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc