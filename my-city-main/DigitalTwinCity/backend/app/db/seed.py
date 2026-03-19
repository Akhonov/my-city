from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.placed_improvement import PlacedImprovement
from app.models.simulation_history import SimulationHistory
from app.models.zone import Zone
from app.services.ai_benefit_service import AIBenefitService
from app.services.scoring_service import ScoringService
from app.services.simulation_engine import SimulationEngine
from app.utils.helpers import dumps_json


def seed_database() -> None:
    db: Session = SessionLocal()
    scoring_service = ScoringService()
    ai_service = AIBenefitService()
    simulation_engine = SimulationEngine()

    try:
        zones = db.query(Zone).order_by(Zone.id.asc()).all()

        if not zones:
            zones = [
                Zone(
                    name="Dense Residential Block A",
                    zone_type="residential",
                    latitude=43.2382,
                    longitude=76.9455,
                    green_area=18,
                    lighting=48,
                    traffic=58,
                    air_quality=54,
                    walkability=57,
                    accessibility=50,
                    safety=47,
                    heat=72,
                    mobility=52,
                    eco_score=44,
                    population_density=84,
                    noise_level=58,
                    public_transport_access=46,
                    barrier_level=42,
                    housing_capacity=32,
                    housing_pressure=78,
                    economic_activity=52,
                    commercial_access=50,
                    social_service_access=42,
                    healthcare_access=38,
                    education_access=45,
                    utility_network_load=74,
                    infrastructure_stability=46,
                    service_capacity=40,
                    attractiveness_score=48,
                    livability_score=44,
                    employment_support=46,
                    public_space_quality=34,
                    environmental_resilience=38,
                    urban_quality_index=0,
                ),
                Zone(
                    name="School and Services Edge",
                    zone_type="school",
                    latitude=43.2393,
                    longitude=76.9471,
                    green_area=34,
                    lighting=38,
                    traffic=46,
                    air_quality=60,
                    walkability=60,
                    accessibility=58,
                    safety=42,
                    heat=56,
                    mobility=54,
                    eco_score=52,
                    population_density=58,
                    noise_level=44,
                    public_transport_access=56,
                    barrier_level=34,
                    housing_capacity=44,
                    housing_pressure=48,
                    economic_activity=40,
                    commercial_access=42,
                    social_service_access=46,
                    healthcare_access=28,
                    education_access=72,
                    utility_network_load=52,
                    infrastructure_stability=58,
                    service_capacity=50,
                    attractiveness_score=52,
                    livability_score=50,
                    employment_support=38,
                    public_space_quality=46,
                    environmental_resilience=48,
                    urban_quality_index=0,
                ),
                Zone(
                    name="Commercial Corridor West",
                    zone_type="commercial",
                    latitude=43.2405,
                    longitude=76.9492,
                    green_area=16,
                    lighting=68,
                    traffic=86,
                    air_quality=40,
                    walkability=64,
                    accessibility=60,
                    safety=58,
                    heat=70,
                    mobility=66,
                    eco_score=42,
                    population_density=66,
                    noise_level=74,
                    public_transport_access=74,
                    barrier_level=28,
                    housing_capacity=28,
                    housing_pressure=52,
                    economic_activity=82,
                    commercial_access=84,
                    social_service_access=48,
                    healthcare_access=46,
                    education_access=44,
                    utility_network_load=76,
                    infrastructure_stability=54,
                    service_capacity=58,
                    attractiveness_score=62,
                    livability_score=48,
                    employment_support=78,
                    public_space_quality=42,
                    environmental_resilience=40,
                    urban_quality_index=0,
                ),
                Zone(
                    name="Underserved Courtyard C",
                    zone_type="parkless_courtyard",
                    latitude=43.2377,
                    longitude=76.9438,
                    green_area=12,
                    lighting=40,
                    traffic=22,
                    air_quality=60,
                    walkability=48,
                    accessibility=26,
                    safety=44,
                    heat=64,
                    mobility=38,
                    eco_score=46,
                    population_density=68,
                    noise_level=34,
                    public_transport_access=34,
                    barrier_level=68,
                    housing_capacity=40,
                    housing_pressure=70,
                    economic_activity=30,
                    commercial_access=28,
                    social_service_access=24,
                    healthcare_access=26,
                    education_access=34,
                    utility_network_load=62,
                    infrastructure_stability=40,
                    service_capacity=28,
                    attractiveness_score=36,
                    livability_score=32,
                    employment_support=26,
                    public_space_quality=22,
                    environmental_resilience=34,
                    urban_quality_index=0,
                ),
                Zone(
                    name="Overloaded Infrastructure Node",
                    zone_type="infrastructure",
                    latitude=43.2369,
                    longitude=76.9510,
                    green_area=10,
                    lighting=36,
                    traffic=78,
                    air_quality=42,
                    walkability=38,
                    accessibility=34,
                    safety=36,
                    heat=68,
                    mobility=50,
                    eco_score=36,
                    population_density=54,
                    noise_level=66,
                    public_transport_access=42,
                    barrier_level=40,
                    housing_capacity=34,
                    housing_pressure=60,
                    economic_activity=48,
                    commercial_access=42,
                    social_service_access=30,
                    healthcare_access=32,
                    education_access=30,
                    utility_network_load=90,
                    infrastructure_stability=28,
                    service_capacity=30,
                    attractiveness_score=34,
                    livability_score=30,
                    employment_support=42,
                    public_space_quality=20,
                    environmental_resilience=24,
                    urban_quality_index=0,
                ),
                Zone(
                    name="Balanced Mixed-Use Center",
                    zone_type="mixed_use",
                    latitude=43.2412,
                    longitude=76.9447,
                    green_area=64,
                    lighting=72,
                    traffic=34,
                    air_quality=78,
                    walkability=80,
                    accessibility=76,
                    safety=74,
                    heat=34,
                    mobility=74,
                    eco_score=78,
                    population_density=46,
                    noise_level=28,
                    public_transport_access=70,
                    barrier_level=16,
                    housing_capacity=62,
                    housing_pressure=34,
                    economic_activity=70,
                    commercial_access=72,
                    social_service_access=74,
                    healthcare_access=70,
                    education_access=68,
                    utility_network_load=42,
                    infrastructure_stability=78,
                    service_capacity=76,
                    attractiveness_score=80,
                    livability_score=82,
                    employment_support=68,
                    public_space_quality=78,
                    environmental_resilience=76,
                    urban_quality_index=0,
                ),
            ]

            for zone in zones:
                zone.urban_quality_index = scoring_service.calculate_urban_quality_index(zone)
                db.add(zone)

            db.commit()
            zones = db.query(Zone).order_by(Zone.id.asc()).all()

        improvements_exist = db.query(PlacedImprovement).first()
        if improvements_exist:
            return

        zone_by_name = {zone.name: zone for zone in zones}

        residential_zone = zone_by_name["Dense Residential Block A"]
        road_zone = zone_by_name["Overloaded Infrastructure Node"]
        courtyard_zone = zone_by_name["Underserved Courtyard C"]
        school_zone = zone_by_name["School and Services Edge"]

        park_analysis = ai_service.analyze(zone=residential_zone, action_type="add_park", local_demand_signal=18.0)
        road_light_analysis = ai_service.analyze(zone=road_zone, action_type="add_lighting", local_demand_signal=14.0)
        ramp_analysis = ai_service.analyze(zone=courtyard_zone, action_type="add_ramp", local_demand_signal=12.0)
        clinic_analysis = ai_service.analyze(zone=school_zone, action_type="add_clinic", local_demand_signal=16.0)
        utility_analysis = ai_service.analyze(zone=road_zone, action_type="upgrade_utilities", local_demand_signal=20.0)

        proposed_park = PlacedImprovement(
            zone_id=residential_zone.id,
            improvement_type="park",
            latitude=43.23835,
            longitude=76.9457,
            title="Pocket Park Proposal",
            description="A proposed pocket park in a dense residential area.",
            status="proposed",
            source="user",
            user_identifier="demo-user-park",
            ai_beneficial=park_analysis.beneficial,
            ai_benefit_score=park_analysis.benefit_score,
            ai_confidence=park_analysis.confidence,
            priority_score=round((park_analysis.benefit_score * 0.7) + (park_analysis.zone_need_score * 0.3), 2),
            hotspot_score=22.0,
            exact_zone_matches_count=1,
            nearby_similar_requests_count=1,
            unique_users_nearby_count=1,
            explanation=park_analysis.explanation,
            tradeoffs=dumps_json(park_analysis.tradeoffs),
            metric_impacts=dumps_json([impact.model_dump() for impact in park_analysis.metric_impacts]),
            metadata_json=dumps_json({"seed": True, "category": "greenery"}),
            geometry_type="Point",
        )

        proposed_light = PlacedImprovement(
            zone_id=road_zone.id,
            improvement_type="street_light",
            latitude=43.23685,
            longitude=76.9512,
            title="Unsafe Corridor Light Point",
            description="A proposed street light in a dark overloaded corridor.",
            status="proposed",
            source="hotspot",
            user_identifier="demo-user-light",
            ai_beneficial=road_light_analysis.beneficial,
            ai_benefit_score=road_light_analysis.benefit_score,
            ai_confidence=road_light_analysis.confidence,
            priority_score=round((road_light_analysis.benefit_score * 0.7) + (road_light_analysis.zone_need_score * 0.3), 2),
            hotspot_score=34.0,
            exact_zone_matches_count=2,
            nearby_similar_requests_count=2,
            unique_users_nearby_count=2,
            explanation=road_light_analysis.explanation,
            tradeoffs=dumps_json(road_light_analysis.tradeoffs),
            metric_impacts=dumps_json([impact.model_dump() for impact in road_light_analysis.metric_impacts]),
            metadata_json=dumps_json({"seed": True, "category": "safety"}),
            geometry_type="Point",
        )

        proposed_clinic = PlacedImprovement(
            zone_id=school_zone.id,
            improvement_type="clinic",
            latitude=43.23915,
            longitude=76.94735,
            title="Neighborhood Clinic Proposal",
            description="A clinic proposal near the school-services edge with weak healthcare access.",
            status="proposed",
            source="user",
            user_identifier="demo-user-clinic",
            ai_beneficial=clinic_analysis.beneficial,
            ai_benefit_score=clinic_analysis.benefit_score,
            ai_confidence=clinic_analysis.confidence,
            priority_score=round((clinic_analysis.benefit_score * 0.7) + (clinic_analysis.zone_need_score * 0.3), 2),
            hotspot_score=30.0,
            exact_zone_matches_count=1,
            nearby_similar_requests_count=1,
            unique_users_nearby_count=1,
            explanation=clinic_analysis.explanation,
            tradeoffs=dumps_json(clinic_analysis.tradeoffs),
            metric_impacts=dumps_json([impact.model_dump() for impact in clinic_analysis.metric_impacts]),
            metadata_json=dumps_json({"seed": True, "category": "healthcare"}),
            geometry_type="Point",
        )

        utility_simulation = simulation_engine.apply_to_zone(road_zone, "upgrade_utilities")
        db.add(road_zone)

        applied_utility_upgrade = PlacedImprovement(
            zone_id=road_zone.id,
            improvement_type="utility_upgrade",
            latitude=43.23695,
            longitude=76.95085,
            title="Applied Utility Upgrade",
            description="A seeded utility upgrade improving network stability in an overloaded zone.",
            status="applied",
            source="simulation",
            user_identifier="demo-admin",
            ai_beneficial=utility_analysis.beneficial,
            ai_benefit_score=utility_analysis.benefit_score,
            ai_confidence=utility_analysis.confidence,
            priority_score=round((utility_analysis.benefit_score * 0.7) + (utility_analysis.zone_need_score * 0.3), 2),
            hotspot_score=28.0,
            exact_zone_matches_count=1,
            nearby_similar_requests_count=1,
            unique_users_nearby_count=1,
            explanation=utility_analysis.explanation,
            tradeoffs=dumps_json(utility_analysis.tradeoffs),
            metric_impacts=dumps_json([impact.model_dump() for impact in utility_analysis.metric_impacts]),
            metadata_json=dumps_json({"seed": True, "category": "networks"}),
            geometry_type="Point",
        )

        ramp_simulation = simulation_engine.apply_to_zone(courtyard_zone, "add_ramp")
        db.add(courtyard_zone)

        applied_ramp = PlacedImprovement(
            zone_id=courtyard_zone.id,
            improvement_type="ramp",
            latitude=43.23765,
            longitude=76.94395,
            title="Applied Courtyard Ramp",
            description="A ramp already applied in the courtyard to reduce barriers.",
            status="applied",
            source="simulation",
            user_identifier="demo-admin",
            ai_beneficial=ramp_analysis.beneficial,
            ai_benefit_score=ramp_analysis.benefit_score,
            ai_confidence=ramp_analysis.confidence,
            priority_score=round((ramp_analysis.benefit_score * 0.7) + (ramp_analysis.zone_need_score * 0.3), 2),
            hotspot_score=18.0,
            exact_zone_matches_count=1,
            nearby_similar_requests_count=0,
            unique_users_nearby_count=1,
            explanation=ramp_analysis.explanation,
            tradeoffs=dumps_json(ramp_analysis.tradeoffs),
            metric_impacts=dumps_json([impact.model_dump() for impact in ramp_analysis.metric_impacts]),
            metadata_json=dumps_json({"seed": True, "category": "accessibility"}),
            geometry_type="Point",
        )

        utility_history = SimulationHistory(
            zone_id=road_zone.id,
            action_type="upgrade_utilities",
            note="Seeded applied improvement: Applied Utility Upgrade",
            before_metrics=dumps_json(utility_simulation["before_metrics"]),
            after_metrics=dumps_json(utility_simulation["after_metrics"]),
            metric_impacts=dumps_json([impact.model_dump() for impact in utility_simulation["metric_impacts"]]),
            before_urban_quality_index=utility_simulation["before_urban_quality_index"],
            after_urban_quality_index=utility_simulation["after_urban_quality_index"],
        )

        ramp_history = SimulationHistory(
            zone_id=courtyard_zone.id,
            action_type="add_ramp",
            note="Seeded applied improvement: Applied Courtyard Ramp",
            before_metrics=dumps_json(ramp_simulation["before_metrics"]),
            after_metrics=dumps_json(ramp_simulation["after_metrics"]),
            metric_impacts=dumps_json([impact.model_dump() for impact in ramp_simulation["metric_impacts"]]),
            before_urban_quality_index=ramp_simulation["before_urban_quality_index"],
            after_urban_quality_index=ramp_simulation["after_urban_quality_index"],
        )

        db.add(proposed_park)
        db.add(proposed_light)
        db.add(proposed_clinic)
        db.add(applied_utility_upgrade)
        db.add(applied_ramp)
        db.add(utility_history)
        db.add(ramp_history)
        db.commit()
    finally:
        db.close()