from collections import defaultdict

from app.models.placed_improvement import PlacedImprovement
from app.models.zone import Zone
from app.schemas.improvement import GeoJSONFeature, GeoJSONFeatureCollection, ImprovementHotspotRegion
from app.services.scoring_service import ScoringService
from app.utils.helpers import loads_json, round2


class GeoJSONService:
    def build_feature_collection(self, improvements: list[PlacedImprovement]) -> GeoJSONFeatureCollection:
        features: list[GeoJSONFeature] = []

        for improvement in improvements:
            metadata_value = loads_json(improvement.metadata_json, default=None) if improvement.metadata_json else None

            features.append(
                GeoJSONFeature(
                    geometry={
                        "type": "Point",
                        "coordinates": [improvement.longitude, improvement.latitude],
                    },
                    properties={
                        "id": improvement.id,
                        "zone_id": improvement.zone_id,
                        "improvement_type": improvement.improvement_type,
                        "title": improvement.title,
                        "description": improvement.description,
                        "status": improvement.status,
                        "source": improvement.source,
                        "user_identifier": improvement.user_identifier,
                        "ai_beneficial": improvement.ai_beneficial,
                        "ai_benefit_score": round2(improvement.ai_benefit_score),
                        "ai_confidence": round2(improvement.ai_confidence),
                        "priority_score": round2(improvement.priority_score),
                        "hotspot_score": round2(improvement.hotspot_score),
                        "exact_zone_matches_count": improvement.exact_zone_matches_count,
                        "nearby_similar_requests_count": improvement.nearby_similar_requests_count,
                        "unique_users_nearby_count": improvement.unique_users_nearby_count,
                        "geometry_type": improvement.geometry_type,
                        "metadata_json": metadata_value,
                        "created_at": improvement.created_at.isoformat(),
                        "updated_at": improvement.updated_at.isoformat(),
                    },
                )
            )

        return GeoJSONFeatureCollection(features=features)

    def build_hotspot_regions(
        self,
        improvements: list[PlacedImprovement],
        zones: list[Zone],
    ) -> list[ImprovementHotspotRegion]:
        zone_map = {zone.id: zone for zone in zones}
        grouped: dict[tuple[int | None, str], list[PlacedImprovement]] = defaultdict(list)

        for improvement in improvements:
            grouped[(improvement.zone_id, improvement.improvement_type)].append(improvement)

        scoring_service = ScoringService()
        regions: list[ImprovementHotspotRegion] = []

        for (zone_id, improvement_type), items in grouped.items():
            zone_name = zone_map[zone_id].name if zone_id in zone_map else "Unassigned Zone"
            center_latitude = sum(item.latitude for item in items) / len(items)
            center_longitude = sum(item.longitude for item in items) / len(items)
            unique_users = {
                item.user_identifier
                for item in items
                if item.user_identifier
            }
            hotspot_score = round2(
                min(
                    (len(items) * 12) + (len(unique_users) * 10),
                    100.0,
                )
            )

            regions.append(
                ImprovementHotspotRegion(
                    improvement_type=improvement_type,
                    zone_id=zone_id,
                    zone_name=zone_name,
                    center_latitude=round2(center_latitude),
                    center_longitude=round2(center_longitude),
                    object_count=len(items),
                    unique_users_count=len(unique_users),
                    hotspot_score=hotspot_score,
                    priority_level=scoring_service.score_to_priority_level(hotspot_score),
                )
            )

        return sorted(regions, key=lambda item: item.hotspot_score, reverse=True)