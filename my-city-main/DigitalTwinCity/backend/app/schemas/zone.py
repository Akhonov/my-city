from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ZoneMetrics(BaseModel):
    green_area: float
    lighting: float
    traffic: float
    air_quality: float
    walkability: float
    accessibility: float
    safety: float
    heat: float
    mobility: float
    eco_score: float
    population_density: float
    noise_level: float
    public_transport_access: float
    barrier_level: float

    housing_capacity: float
    housing_pressure: float
    economic_activity: float
    commercial_access: float
    social_service_access: float
    healthcare_access: float
    education_access: float
    utility_network_load: float
    infrastructure_stability: float
    service_capacity: float
    attractiveness_score: float
    livability_score: float
    employment_support: float
    public_space_quality: float
    environmental_resilience: float


class ZoneResponse(ZoneMetrics):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    zone_type: str
    latitude: float
    longitude: float
    urban_quality_index: float
    created_at: datetime
    updated_at: datetime