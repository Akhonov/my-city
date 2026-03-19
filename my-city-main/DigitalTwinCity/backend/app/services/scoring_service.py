from app.models.zone import Zone
from app.utils.constants import NEGATIVE_METRICS, POSITIVE_METRICS
from app.utils.helpers import clamp, round2


class ScoringService:
    @staticmethod
    def calculate_urban_quality_index(zone: Zone | dict) -> float:
        if isinstance(zone, dict):
            zone_data = zone
        else:
            zone_data = {
                field: getattr(zone, field)
                for field in list(POSITIVE_METRICS) + list(NEGATIVE_METRICS)
            }

        score = 0.0

        for metric, weight in POSITIVE_METRICS.items():
            score += float(zone_data.get(metric, 0.0)) * weight

        for metric, weight in NEGATIVE_METRICS.items():
            score += (100.0 - float(zone_data.get(metric, 0.0))) * weight

        return round2(clamp(score, 0.0, 100.0))

    @staticmethod
    def calculate_zone_need_score(zone: Zone) -> float:
        need_signals = [
            100.0 - zone.green_area,
            100.0 - zone.lighting,
            zone.traffic,
            100.0 - zone.air_quality,
            100.0 - zone.walkability,
            100.0 - zone.accessibility,
            100.0 - zone.safety,
            zone.heat,
            100.0 - zone.mobility,
            100.0 - zone.eco_score,
            zone.noise_level,
            100.0 - zone.public_transport_access,
            zone.barrier_level,
            100.0 - zone.housing_capacity,
            zone.housing_pressure,
            100.0 - zone.economic_activity,
            100.0 - zone.commercial_access,
            100.0 - zone.social_service_access,
            100.0 - zone.healthcare_access,
            100.0 - zone.education_access,
            zone.utility_network_load,
            100.0 - zone.infrastructure_stability,
            100.0 - zone.service_capacity,
            100.0 - zone.attractiveness_score,
            100.0 - zone.livability_score,
            100.0 - zone.employment_support,
            100.0 - zone.public_space_quality,
            100.0 - zone.environmental_resilience,
        ]
        return round2(sum(need_signals) / len(need_signals))

    @staticmethod
    def calculate_resilience_score(zone: Zone | dict) -> float:
        if isinstance(zone, dict):
            zone_data = zone
        else:
            zone_data = {
                "infrastructure_stability": zone.infrastructure_stability,
                "environmental_resilience": zone.environmental_resilience,
                "service_capacity": zone.service_capacity,
                "utility_network_load": zone.utility_network_load,
                "heat": zone.heat,
                "barrier_level": zone.barrier_level,
            }

        score = (
            (float(zone_data.get("infrastructure_stability", 0.0)) * 0.30)
            + (float(zone_data.get("environmental_resilience", 0.0)) * 0.25)
            + (float(zone_data.get("service_capacity", 0.0)) * 0.20)
            + ((100.0 - float(zone_data.get("utility_network_load", 0.0))) * 0.15)
            + ((100.0 - float(zone_data.get("heat", 0.0))) * 0.05)
            + ((100.0 - float(zone_data.get("barrier_level", 0.0))) * 0.05)
        )
        return round2(clamp(score, 0.0, 100.0))

    @staticmethod
    def score_to_priority_level(score: float) -> str:
        if score >= 85:
            return "critical"
        if score >= 70:
            return "high"
        if score >= 50:
            return "medium"
        return "low"