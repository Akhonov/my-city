from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="Almaty Twin City API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    "residential": "Жилой квартал",
    "mixedUse": "Mixed-use кластер",
    "park": "Городской парк",
    "school": "Школа / STEM",
    "hospital": "Медицинский центр",
    "transit": "Transit hub",
    "energy": "Энергоцентр",
}

METRIC_LABELS = {
    "air": "Воздух",
    "traffic": "Трафик",
    "green": "Озеленение",
    "housing": "Жилье",
    "economy": "Экономика",
    "social": "Соцсервисы",
    "utility": "Сети",
    "resilience": "Устойчивость",
}

SITES = {
    "site-abay-river": {
        "name": "Abay Riverfront",
        "district": "historic-core",
        "context": {
            "transitAccess": 0.9,
            "roadAccess": 0.8,
            "currentPressure": 0.86,
            "greenDeficit": 0.58,
            "socialDeficit": 0.42,
            "utilityCapacity": 0.58,
            "seismicConstraint": 0.68,
        },
    },
    "site-west-housing": {
        "name": "Auezov Growth Parcel",
        "district": "west-growth",
        "context": {
            "transitAccess": 0.55,
            "roadAccess": 0.78,
            "currentPressure": 0.48,
            "greenDeficit": 0.72,
            "socialDeficit": 0.84,
            "utilityCapacity": 0.66,
            "seismicConstraint": 0.38,
        },
    },
    "site-esentai-mix": {
        "name": "Esentai East Lot",
        "district": "esentai",
        "context": {
            "transitAccess": 0.74,
            "roadAccess": 0.92,
            "currentPressure": 0.82,
            "greenDeficit": 0.46,
            "socialDeficit": 0.36,
            "utilityCapacity": 0.71,
            "seismicConstraint": 0.59,
        },
    },
    "site-foothill-clinic": {
        "name": "Foothill Wellness Node",
        "district": "south-foothill",
        "context": {
            "transitAccess": 0.44,
            "roadAccess": 0.67,
            "currentPressure": 0.34,
            "greenDeficit": 0.31,
            "socialDeficit": 0.76,
            "utilityCapacity": 0.63,
            "seismicConstraint": 0.82,
        },
    },
    "site-north-utility": {
        "name": "North Utility Reserve",
        "district": "north-logistics",
        "context": {
            "transitAccess": 0.38,
            "roadAccess": 0.88,
            "currentPressure": 0.41,
            "greenDeficit": 0.63,
            "socialDeficit": 0.52,
            "utilityCapacity": 0.85,
            "seismicConstraint": 0.29,
        },
    },
    "site-sairan-transit": {
        "name": "Sairan Mobility Gate",
        "district": "west-growth",
        "context": {
            "transitAccess": 0.91,
            "roadAccess": 0.84,
            "currentPressure": 0.74,
            "greenDeficit": 0.54,
            "socialDeficit": 0.45,
            "utilityCapacity": 0.62,
            "seismicConstraint": 0.36,
        },
    },
}


class Placement(BaseModel):
    site_id: str
    type_id: str


class CityScenario(BaseModel):
    placements: List[Placement]


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


def describe_placement(site_id: str, site: Dict, type_id: str, impact: Dict[str, float]) -> Dict[str, str]:
    messages: List[str] = []

    if type_id == "transit" and impact["traffic"] <= -12:
        messages.append("разгружает магистрали и усиливает общественный транспорт")
    if type_id == "park" and impact["green"] >= 20:
        messages.append("компенсирует дефицит зелени в перегретом районе")
    if type_id == "hospital" and impact["social"] >= 20:
        messages.append("закрывает серьезный дефицит медуслуг в районе")
    if type_id == "school" and impact["social"] >= 20:
        messages.append("снимает давление на существующие школы и секции")
    if type_id in {"residential", "mixedUse"} and impact["traffic"] >= 10:
        messages.append("требует компенсации трафика через BRT и parking policy")
    if site["context"]["seismicConstraint"] > 0.75:
        messages.append("нужны усиленные сейсмостандарты и ограничение по высоте")

    return {
        "siteId": site_id,
        "siteName": site["name"],
        "district": site["district"],
        "typeId": type_id,
        "typeLabel": TYPE_LABELS[type_id],
        "effect": "; ".join(messages) if messages else "дает сбалансированный эффект без критичных перекосов",
    }


def suggest_type(site: Dict) -> str:
    context = site["context"]
    if context["socialDeficit"] > 0.75:
        return "school"
    if context["transitAccess"] > 0.85:
        return "transit"
    if context["greenDeficit"] > 0.65:
        return "park"
    return "mixedUse"


def simulate(payload: CityScenario) -> Dict:
    metrics = BASELINE_METRICS.copy()
    deltas = {metric: 0.0 for metric in metrics.keys()}
    placements = []

    for placement in payload.placements:
        if placement.site_id not in SITES or placement.type_id not in TYPE_IMPACTS:
            continue

        site = SITES[placement.site_id]
        impact = compute_adjusted_impact(placement.type_id, site)
        placements.append(describe_placement(placement.site_id, site, placement.type_id, impact))

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

    warnings: List[str] = []
    if metrics["traffic"] > 82:
        warnings.append("Трафик выходит в красную зону: нужны transit-first меры.")
    if metrics["air"] < 52:
        warnings.append("Качество воздуха ухудшается: компенсируйте парками и снижением автотрафика.")
    if metrics["utility"] > 80:
        warnings.append("Инженерные сети перегружаются: добавьте энергоцентр или phased rollout.")
    if metrics["resilience"] < 55:
        warnings.append("Устойчивость снижается: усилите сейсмостойкость и эвакуационные сценарии.")

    opportunities: List[str] = []
    if metrics["green"] > BASELINE_METRICS["green"] + 8:
        opportunities.append("Сценарий улучшает микроклимат и снижает heat island.")
    if metrics["social"] > BASELINE_METRICS["social"] + 8:
        opportunities.append("Новые соцобъекты повышают доступность сервиса по районам.")
    if metrics["economy"] > BASELINE_METRICS["economy"] + 8:
        opportunities.append("Экономический потенциал растет без потери управляемости.")
    if metrics["housing"] > BASELINE_METRICS["housing"] + 8:
        opportunities.append("Сценарий расширяет предложение жилья в дефицитных кластерах.")

    strongest_metric = max(
        ((metric, value) for metric, value in deltas.items() if metric not in {"traffic", "utility"}),
        key=lambda item: abs(item[1]),
        default=("economy", 0),
    )

    summary = (
        "Выберите участок и тип объекта. Система покажет влияние на воздух, трафик, сети и устойчивость."
        if not placements
        else f"Сценарий включает {len(placements)} новых объекта(ов). Самое сильное изменение: "
             f"{METRIC_LABELS[strongest_metric[0]]} "
             f"{'улучшается' if strongest_metric[1] >= 0 else 'ухудшается'} "
             f"на {abs(round(strongest_metric[1]))} п."
    )

    ranked_sites = []
    for site_id, site in SITES.items():
        suggested_type = suggest_type(site)
        projected = compute_adjusted_impact(suggested_type, site)
        context = site["context"]
        suitability = clamp(
            72
            + context["transitAccess"] * (18 if suggested_type == "transit" else 6)
            + context["greenDeficit"] * (16 if suggested_type == "park" else 0)
            + context["socialDeficit"] * (18 if suggested_type in {"school", "hospital"} else 4)
            + context["utilityCapacity"] * (12 if suggested_type == "energy" else 4)
            - context["currentPressure"] * (12 if suggested_type in {"mixedUse", "residential"} else 4)
            - context["seismicConstraint"] * (10 if suggested_type == "mixedUse" else 5)
        )
        ranked_sites.append(
            {
                "siteId": site_id,
                "siteName": site["name"],
                "suggestedType": suggested_type,
                "suggestedTypeLabel": TYPE_LABELS[suggested_type],
                "suitability": suitability,
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


@app.post("/api/simulate")
async def simulate_city(scenario: CityScenario) -> Dict:
    return simulate(scenario)


@app.get("/api/health")
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok", "service": "almaty-twin-city-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
