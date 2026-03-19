from app.models.zone import Zone
from app.schemas.suggestion import BenefitAnalysisResponse, BenefitMetricImpact
from app.services.scoring_service import ScoringService
from app.utils.constants import ACTION_DEFINITIONS, ZONE_TYPE_WEIGHTS
from app.utils.helpers import clamp, round2


class AIBenefitService:
    def __init__(self) -> None:
        self.scoring_service = ScoringService()

    def analyze(
        self,
        zone: Zone,
        action_type: str,
        local_demand_signal: float = 0.0,
    ) -> BenefitAnalysisResponse:
        if action_type not in ACTION_DEFINITIONS:
            raise ValueError(f"Unsupported action_type: {action_type}")

        zone_need_score = self.scoring_service.calculate_zone_need_score(zone)
        base_score = 35.0
        confidence = 65.0
        reasons: list[str] = []
        tradeoffs: list[str] = list(ACTION_DEFINITIONS[action_type]["downsides"])

        zone_type_weight = ZONE_TYPE_WEIGHTS.get(zone.zone_type, {}).get(action_type, 1.0)
        metric_impacts = self._metric_impacts(action_type)

        if action_type == "add_park":
            if zone.green_area < 35:
                base_score += 18
                confidence += 6
                reasons.append("green coverage is low")
            if zone.heat > 60:
                base_score += 12
                reasons.append("heat is elevated")
            if zone.population_density > 55:
                base_score += 8
                reasons.append("population density is high enough to support shared public green space")
            if zone.public_space_quality < 55:
                base_score += 8
                reasons.append("public-space quality is weak")
            if zone.green_area > 75:
                base_score -= 18
                reasons.append("existing green coverage is already strong")

        elif action_type == "add_lighting":
            if zone.lighting < 45:
                base_score += 20
                confidence += 8
                reasons.append("lighting is currently weak")
            if zone.safety < 50:
                base_score += 15
                confidence += 6
                reasons.append("safety conditions are below target")
            if zone.walkability < 55:
                base_score += 6
                reasons.append("pedestrian comfort is limited")
            if zone.lighting > 80:
                base_score -= 20
                reasons.append("lighting is already adequate")

        elif action_type == "add_bike_lane":
            if zone.mobility < 55:
                base_score += 12
                reasons.append("mobility is below target")
            if 40 <= zone.traffic <= 80:
                base_score += 10
                reasons.append("traffic level suggests a modal-shift opportunity")
            if zone.eco_score < 55:
                base_score += 5
                reasons.append("environmental mobility options are limited")
            if zone.traffic > 85 and zone.zone_type == "road":
                base_score -= 10
                reasons.append("very high traffic may require careful design to avoid conflicts")

        elif action_type == "add_ramp":
            if zone.accessibility < 50:
                base_score += 20
                confidence += 8
                reasons.append("accessibility is weak")
            if zone.barrier_level > 50:
                base_score += 18
                confidence += 5
                reasons.append("barrier level is high")
            if zone.livability_score < 55:
                base_score += 4
                reasons.append("inclusive urban usability is below target")
            if zone.accessibility > 85 and zone.barrier_level < 20:
                base_score -= 18
                reasons.append("the area is already highly accessible")

        elif action_type == "add_bus_stop":
            if zone.public_transport_access < 45:
                base_score += 20
                confidence += 7
                reasons.append("public transport access is limited")
            if zone.mobility < 55:
                base_score += 10
                reasons.append("mobility can be improved")
            if zone.commercial_access < 50 or zone.social_service_access < 50:
                base_score += 6
                reasons.append("local access to services would benefit from better transit")
            if zone.public_transport_access > 80:
                base_score -= 20
                reasons.append("public transport access is already strong")

        elif action_type == "reduce_traffic":
            if zone.traffic > 60:
                base_score += 18
                confidence += 6
                reasons.append("traffic burden is high")
            if zone.noise_level > 55:
                base_score += 8
                reasons.append("noise is elevated")
            if zone.air_quality < 55:
                base_score += 8
                reasons.append("air quality can improve through traffic reduction")
            if zone.livability_score < 55:
                base_score += 5
                reasons.append("livability is held back by corridor conditions")
            if zone.traffic < 30:
                base_score -= 15
                reasons.append("traffic is already relatively low")

        elif action_type == "remove_barriers":
            if zone.barrier_level > 55:
                base_score += 18
                confidence += 6
                reasons.append("barrier level is high")
            if zone.accessibility < 60:
                base_score += 14
                reasons.append("accessibility is below target")
            if zone.barrier_level < 20 and zone.accessibility > 80:
                base_score -= 14
                reasons.append("barriers are already limited")

        elif action_type == "add_pedestrian_crossing":
            if zone.safety < 55:
                base_score += 16
                reasons.append("pedestrian safety needs improvement")
            if zone.walkability < 60:
                base_score += 10
                reasons.append("walkability is below target")
            if zone.zone_type in {"school", "road", "commercial"}:
                base_score += 8
                reasons.append("zone type has strong pedestrian movement needs")

        elif action_type == "add_public_benches":
            if zone.walkability < 60:
                base_score += 10
                reasons.append("comfort for walking routes can improve")
            if zone.public_space_quality < 60:
                base_score += 8
                reasons.append("public-space quality is modest")
            if zone.zone_type in {"residential", "courtyard", "park", "commercial"}:
                base_score += 6
                reasons.append("the area supports lingering or short resting use")

        elif action_type == "add_waste_bins":
            if zone.eco_score < 60:
                base_score += 12
                reasons.append("environmental performance can improve")
            if zone.public_space_quality < 60:
                base_score += 5
                reasons.append("cleanliness-related public-space quality can improve")
            if zone.zone_type in {"commercial", "park", "school", "residential"}:
                base_score += 6
                reasons.append("zone usage pattern supports regular waste-bin demand")

        elif action_type == "add_residential_building":
            if zone.housing_capacity < 50:
                base_score += 18
                confidence += 7
                reasons.append("housing capacity is limited")
            if zone.housing_pressure > 60:
                base_score += 18
                confidence += 5
                reasons.append("housing pressure is high")
            if zone.service_capacity < 45:
                base_score -= 10
                reasons.append("service capacity is already constrained")
            if zone.utility_network_load > 70:
                base_score -= 12
                reasons.append("utility networks are already heavily loaded")
            if zone.infrastructure_stability < 45:
                base_score -= 8
                reasons.append("infrastructure stability is weak")
            if zone.economic_activity < 50:
                base_score += 4
                reasons.append("additional residents can support local economic activity")

        elif action_type == "add_commercial_building":
            if zone.economic_activity < 55:
                base_score += 18
                confidence += 6
                reasons.append("economic activity is underpowered")
            if zone.commercial_access < 55:
                base_score += 15
                reasons.append("commercial access is limited")
            if zone.employment_support < 55:
                base_score += 8
                reasons.append("local employment support is modest")
            if zone.traffic > 80:
                base_score -= 10
                reasons.append("traffic is already severe")
            if zone.utility_network_load > 75:
                base_score -= 8
                reasons.append("utility network load is already high")

        elif action_type == "add_clinic":
            if zone.healthcare_access < 50:
                base_score += 22
                confidence += 8
                reasons.append("healthcare access is weak")
            if zone.social_service_access < 55:
                base_score += 10
                reasons.append("social support coverage is limited")
            if zone.livability_score < 60:
                base_score += 6
                reasons.append("livability can improve through better health access")
            if zone.healthcare_access > 80:
                base_score -= 18
                reasons.append("healthcare access is already strong")

        elif action_type == "add_school":
            if zone.education_access < 50:
                base_score += 22
                confidence += 8
                reasons.append("education access is weak")
            if zone.social_service_access < 55:
                base_score += 8
                reasons.append("community service coverage is limited")
            if zone.attractiveness_score < 55:
                base_score += 4
                reasons.append("family-oriented attractiveness is modest")
            if zone.education_access > 80:
                base_score -= 18
                reasons.append("education access is already strong")

        elif action_type == "add_social_service_center":
            if zone.social_service_access < 50:
                base_score += 22
                confidence += 8
                reasons.append("social service access is weak")
            if zone.service_capacity < 55:
                base_score += 10
                reasons.append("service capacity is limited")
            if zone.livability_score < 60:
                base_score += 6
                reasons.append("livability would benefit from better support services")

        elif action_type == "upgrade_utilities":
            if zone.utility_network_load > 60:
                base_score += 22
                confidence += 8
                reasons.append("utility network load is high")
            if zone.infrastructure_stability < 55:
                base_score += 18
                confidence += 6
                reasons.append("infrastructure stability is weak")
            if zone.service_capacity < 55:
                base_score += 8
                reasons.append("service capacity is constrained")
            if zone.environmental_resilience < 55:
                base_score += 6
                reasons.append("environmental resilience can improve")
            if zone.utility_network_load < 30 and zone.infrastructure_stability > 80:
                base_score -= 12
                reasons.append("network conditions are already relatively strong")

        elif action_type == "add_green_roof":
            if zone.heat > 55:
                base_score += 14
                reasons.append("heat stress is elevated")
            if zone.green_area < 45:
                base_score += 10
                reasons.append("green coverage is limited")
            if zone.environmental_resilience < 60:
                base_score += 8
                reasons.append("resilience to environmental stress can improve")

        elif action_type == "add_public_square":
            if zone.public_space_quality < 55:
                base_score += 18
                reasons.append("public-space quality is weak")
            if zone.walkability < 60:
                base_score += 10
                reasons.append("walkability can improve")
            if zone.attractiveness_score < 60:
                base_score += 10
                reasons.append("the area needs stronger public identity and appeal")

        elif action_type == "add_playground":
            if zone.public_space_quality < 60:
                base_score += 12
                reasons.append("public-space quality is modest")
            if zone.social_service_access < 60:
                base_score += 6
                reasons.append("family-oriented community support is limited")
            if zone.zone_type in {"residential", "courtyard", "parkless_courtyard", "park"}:
                base_score += 8
                reasons.append("zone type strongly supports recreation needs")

        elif action_type == "add_ev_charging":
            if zone.environmental_resilience < 60:
                base_score += 8
                reasons.append("low-emission infrastructure can improve resilience")
            if zone.economic_activity > 40:
                base_score += 6
                reasons.append("local activity can support charging demand")
            if zone.utility_network_load > 75:
                base_score -= 12
                reasons.append("utility network load is already high")

        elif action_type == "add_water_feature":
            if zone.heat > 60:
                base_score += 14
                reasons.append("heat is elevated")
            if zone.public_space_quality < 60:
                base_score += 8
                reasons.append("public-space amenity quality is limited")
            if zone.attractiveness_score < 60:
                base_score += 8
                reasons.append("the area would benefit from stronger placemaking")

        elif action_type == "add_community_center":
            if zone.social_service_access < 55:
                base_score += 18
                confidence += 7
                reasons.append("social service access is weak")
            if zone.livability_score < 60:
                base_score += 10
                reasons.append("livability is below target")
            if zone.public_space_quality < 60:
                base_score += 8
                reasons.append("community gathering infrastructure is limited")
            if zone.attractiveness_score < 60:
                base_score += 6
                reasons.append("local attractiveness can improve through civic space")

        demand_bonus = min(local_demand_signal * 0.12, 12.0)
        if demand_bonus > 0:
            base_score += demand_bonus
            reasons.append("repeated nearby community requests support this intervention")

        base_score = base_score * zone_type_weight
        confidence += min(local_demand_signal * 0.05, 10.0)

        benefit_score = round2(clamp(base_score))
        confidence = round2(clamp(confidence))
        priority_level = self.scoring_service.score_to_priority_level((benefit_score * 0.7) + (zone_need_score * 0.3))
        beneficial = benefit_score >= 50

        explanation = self._build_explanation(
            zone=zone,
            action_type=action_type,
            benefit_score=benefit_score,
            reasons=reasons,
        )

        return BenefitAnalysisResponse(
            beneficial=beneficial,
            benefit_score=benefit_score,
            confidence=confidence,
            priority_level=priority_level,
            zone_need_score=round2(zone_need_score),
            explanation=explanation,
            metric_impacts=metric_impacts,
            tradeoffs=tradeoffs,
        )

    def _metric_impacts(self, action_type: str) -> list[BenefitMetricImpact]:
        impacts: list[BenefitMetricImpact] = []
        for metric, delta in ACTION_DEFINITIONS[action_type]["delta"].items():
            impacts.append(
                BenefitMetricImpact(
                    metric=metric,
                    delta=round2(abs(delta)),
                    direction="increase" if delta > 0 else "decrease",
                )
            )
        return impacts

    def _build_explanation(
        self,
        zone: Zone,
        action_type: str,
        benefit_score: float,
        reasons: list[str],
    ) -> str:
        if benefit_score >= 80:
            prefix = "Highly beneficial"
        elif benefit_score >= 60:
            prefix = "Moderately beneficial"
        elif benefit_score >= 45:
            prefix = "Mixed benefit"
        else:
            prefix = "Low benefit"

        action_label = action_type.replace("_", " ")
        zone_label = zone.zone_type.replace("_", " ")
        if reasons:
            reasons_text = ", ".join(reasons[:4])
            return f"{prefix} because {action_label} addresses conditions in this {zone_label} zone where {reasons_text}."
        return f"{prefix} for this {zone_label} zone based on current environmental, housing, service, and infrastructure conditions."