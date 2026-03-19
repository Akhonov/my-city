from enum import Enum


class ZoneType(str, Enum):
    residential = "residential"
    school = "school"
    commercial = "commercial"
    road = "road"
    courtyard = "courtyard"
    park = "park"
    parkless_courtyard = "parkless_courtyard"
    mixed_use = "mixed_use"
    infrastructure = "infrastructure"
    healthcare = "healthcare"
    education = "education"


class ImprovementType(str, Enum):
    add_park = "add_park"
    add_lighting = "add_lighting"
    add_bike_lane = "add_bike_lane"
    add_ramp = "add_ramp"
    add_bus_stop = "add_bus_stop"
    reduce_traffic = "reduce_traffic"
    remove_barriers = "remove_barriers"
    add_pedestrian_crossing = "add_pedestrian_crossing"
    add_public_benches = "add_public_benches"
    add_waste_bins = "add_waste_bins"
    add_residential_building = "add_residential_building"
    add_commercial_building = "add_commercial_building"
    add_clinic = "add_clinic"
    add_school = "add_school"
    add_social_service_center = "add_social_service_center"
    upgrade_utilities = "upgrade_utilities"
    add_green_roof = "add_green_roof"
    add_public_square = "add_public_square"
    add_playground = "add_playground"
    add_ev_charging = "add_ev_charging"
    add_water_feature = "add_water_feature"
    add_community_center = "add_community_center"


class PriorityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"