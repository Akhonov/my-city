from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["simulation"])

BASELINE_METRICS: Dict[str, int] = {
    "air": 63,
    "traffic": 69,
    "green": 48,
    "housing": 57,
    "economy": 72,
    "social": 61,
    "utility": 64,
    "resilience": 58,
}

TYPE_IMPACTS: Dict[str, Dict[str, float]] = {
    "residential": {"air": -3, "traffic": 8, "green": -2, "housing": 14, "economy": 6, "social": 2, "utility": 9, "resilience": -1},
    "mixedUse": {"air": -2, "traffic": 7, "green": -1, "housing": 6, "economy": 14, "social": 3, "utility": 6, "resilience": 0},
    "park": {"air": 8, "traffic": -3, "green": 16, "housing": 0, "economy": 2, "social": 8, "utility": -3, "resilience": 4},
    "school": {"air": 1, "traffic": 2, "green": 1, "housing": 0, "economy": 3, "social": 14, "utility": 4, "resilience": 3},
    "hospital": {"air": 0, "traffic": 3, "green": 0, "housing": 0, "economy": 4, "social": 15, "utility": 5, "resilience": 9},
    "transit": {"air": 4, "traffic": -12, "green": 1, "housing": 0, "economy": 6, "social": 5, "utility": 3, "resilience": 5},
    "energy": {"air": -6, "traffic": 4, "green": -2, "housing": 0, "economy": 8, "social": 0, "utility": 16, "resilience": 4},
}

TYPE_LABELS = {
    "residential": "Residential Block",
    "mixedUse": "Mixed-use Cluster",
    "park": "Urban Park",
    "school": "School / STEM Hub",
    "hospital": "Medical Center",
    "transit": "Transit Hub",
    "energy": "Energy Center",
}

METRIC_LABELS = {
    "air": "Air",
    "traffic": "Traffic",
    "green": "Green",
    "housing": "Housing",
    "economy": "Economy",
    "social": "Social",
    "utility": "Utility",
    "resilience": "Resilience",
}

SITES = {
    "site-abay-river": {"name": "Abay Riverfront", "district": "historic-core", "context": {"transitAccess": 0.9, "roadAccess": 0.8, "currentPressure": 0.86, "greenDeficit": 0.58, "socialDeficit": 0.42, "utilityCapacity": 0.58, "seismicConstraint": 0.68}},
    "site-west-housing": {"name": "Auezov Growth Parcel", "district": "west-growth", "context": {"transitAccess": 0.55, "roadAccess": 0.78, "currentPressure": 0.48, "greenDeficit": 0.72, "socialDeficit": 0.84, "utilityCapacity": 0.66, "seismicConstraint": 0.38}},
    "site-esentai-mix": {"name": "Esentai East Lot", "district": "esentai", "context": {"transitAccess": 0.74, "roadAccess": 0.92, "currentPressure": 0.82, "greenDeficit": 0.46, "socialDeficit": 0.36, "utilityCapacity": 0.71, "seismicConstraint": 0.59}},
    "site-foothill-clinic": {"name": "Foothill Wellness Node", "district": "south-foothill", "context": {"transitAccess": 0.44, "roadAccess": 0.67, "currentPressure": 0.34, "greenDeficit": 0.31, "socialDeficit": 0.76, "utilityCapacity": 0.63, "seismicConstraint": 0.82}},
    "site-north-utility": {"name": "North Utility Reserve", "district": "north-logistics", "context": {"transitAccess": 0.38, "roadAccess": 0.88, "currentPressure": 0.41, "greenDeficit": 0.63, "socialDeficit": 0.52, "utilityCapacity": 0.85, "seismicConstraint": 0.29}},
    "site-sairan-transit": {"name": "Sairan Mobility Gate", "district": "west-growth", "context": {"transitAccess": 0.91, "roadAccess": 0.84, "currentPressure": 0.74, "greenDeficit": 0.54, "socialDeficit": 0.45, "utilityCapacity": 0.62, "seismicConstraint": 0.36}},
}


class Placement(BaseModel):
    site_id: str
    type_id: str


class CityScenario(BaseModel):
    placements: list[Placement]


def clamp(value: float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, round(value)))


def compute_adjusted_impact(type_id: str, site: Dict) -> Dict[str, float]:
    base = TYPE_IMPACTS[type_id].copy()
    context = site["context"]
    base["traffic"] += context["currentPressure"] * (7 if type_id in {"residential", "mixedUse"} else 2)
    base["traffic"] -= context["transitAccess"] * (8 if type_id == "transit" else 1)
    base["air"] -= context["currentPressure"] * (3 if type_id == "energy" else 1.5)
    base["green"] += context["greenDeficit"] * (10 if type_id == "park" else 0)
    base["social"] += context["socialDeficit"] * (10 if type_id in {"school", "hospital"} else 1)
    base["housing"] += context["socialDeficit"] * (3 if type_id == "residential" else 0)
    base["economy"] += context["roadAccess"] * (4 if type_id in {"mixedUse", "energy"} else 1.5)
    base["utility"] += (1 - context["utilityCapacity"]) * (5 if type_id == "energy" else 3)
    base["resilience"] -= context["seismicConstraint"] * (3.5 if type_id in {"energy", "mixedUse"} else 1.5)
    base["resilience"] += context["seismicConstraint"] * (2 if type_id == "hospital" else 0)
    return base


def suggest_type(site: Dict) -> str:
    context = site["context"]
    if context["socialDeficit"] > 0.75:
        return "school"
    if context["transitAccess"] > 0.85:
        return "transit"
    if context["greenDeficit"] > 0.65:
        return "park"
    return "mixedUse"


@router.post("/simulate", summary="Simulate city scenario")
def simulate_city(payload: CityScenario) -> Dict:
    metrics = BASELINE_METRICS.copy()
    deltas = {metric: 0.0 for metric in metrics.keys()}
    placements = []

    for placement in payload.placements:
        if placement.site_id not in SITES or placement.type_id not in TYPE_IMPACTS:
            continue

        site = SITES[placement.site_id]
        impact = compute_adjusted_impact(placement.type_id, site)
        placements.append(
            {
                "siteId": placement.site_id,
                "siteName": site["name"],
                "district": site["district"],
                "typeId": placement.type_id,
                "typeLabel": TYPE_LABELS[placement.type_id],
                "effect": "connected through DigitalTwinCity backend",
            }
        )

        for metric in metrics.keys():
            deltas[metric] += impact.get(metric, 0.0)

    for metric, base_value in BASELINE_METRICS.items():
        metrics[metric] = clamp(base_value + deltas[metric])

    normalized_traffic = clamp(100 - metrics["traffic"])
    normalized_utility = clamp(100 - metrics["utility"])
    score = clamp(
        metrics["air"] * 0.15
        + normalized_traffic * 0.18
        + metrics["green"] * 0.12
        + metrics["housing"] * 0.12
        + metrics["economy"] * 0.15
        + metrics["social"] * 0.11
        + normalized_utility * 0.07
        + metrics["resilience"] * 0.1
    )

    warnings = []
    if metrics["traffic"] > 82:
        warnings.append("Traffic is in the red zone and needs transit-first mitigation.")
    if metrics["air"] < 52:
        warnings.append("Air quality drops and should be offset with more green space.")
    if metrics["utility"] > 80:
        warnings.append("Utility load is high and needs staged rollout or energy support.")
    if metrics["resilience"] < 55:
        warnings.append("Urban resilience is dropping and needs stronger seismic planning.")

    opportunities = []
    if metrics["green"] > BASELINE_METRICS["green"] + 8:
        opportunities.append("The scenario improves microclimate and green coverage.")
    if metrics["social"] > BASELINE_METRICS["social"] + 8:
        opportunities.append("New social infrastructure improves service access.")
    if metrics["economy"] > BASELINE_METRICS["economy"] + 8:
        opportunities.append("Economic potential improves without losing balance.")

    strongest_metric = max(deltas.items(), key=lambda item: abs(item[1]), default=("economy", 0))
    summary = (
        "Choose a site and object type to simulate impact on city metrics."
        if not placements
        else f"Scenario includes {len(placements)} new objects. Strongest change: {METRIC_LABELS[strongest_metric[0]]} by {abs(round(strongest_metric[1]))} pts."
    )

    ranked_sites = []
    for site_id, site in SITES.items():
        suggested_type = suggest_type(site)
        projected = compute_adjusted_impact(suggested_type, site)
        ranked_sites.append(
            {
                "siteId": site_id,
                "siteName": site["name"],
                "suggestedType": suggested_type,
                "suggestedTypeLabel": TYPE_LABELS[suggested_type],
                "suitability": clamp(80 + projected["social"] - projected["traffic"]),
                "quickImpact": {metric: round(value) for metric, value in projected.items()},
            }
        )
    ranked_sites.sort(key=lambda item: item["suitability"], reverse=True)

    return {
        "metrics": metrics,
        "baseline": BASELINE_METRICS,
        "deltas": {metric: round(value) for metric, value in deltas.items()},
        "score": score,
        "warnings": warnings,
        "opportunities": opportunities,
        "summary": summary,
        "placements": placements,
        "rankedSites": ranked_sites,
    }
