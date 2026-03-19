from copy import deepcopy

from app.models.zone import Zone
from app.schemas.simulation import MetricImpact
from app.services.scoring_service import ScoringService
from app.utils.constants import ACTION_DEFINITIONS, METRIC_FIELDS
from app.utils.helpers import clamp, round2


class SimulationEngine:
    def __init__(self) -> None:
        self.scoring_service = ScoringService()

    def get_zone_metrics(self, zone: Zone) -> dict:
        return {field: round2(getattr(zone, field)) for field in METRIC_FIELDS}

    def simulate(self, zone: Zone, action_type: str) -> dict:
        if action_type not in ACTION_DEFINITIONS:
            raise ValueError(f"Unsupported action_type: {action_type}")

        before_metrics = self.get_zone_metrics(zone)
        after_metrics = deepcopy(before_metrics)

        for metric, delta in ACTION_DEFINITIONS[action_type]["delta"].items():
            after_metrics[metric] = round2(clamp(after_metrics[metric] + delta))

        before_index = self.scoring_service.calculate_urban_quality_index(before_metrics)
        after_index = self.scoring_service.calculate_urban_quality_index(after_metrics)

        metric_impacts = self._build_metric_impacts(before_metrics, after_metrics)

        return {
            "before_metrics": before_metrics,
            "after_metrics": after_metrics,
            "metric_impacts": metric_impacts,
            "before_urban_quality_index": before_index,
            "after_urban_quality_index": after_index,
        }

    def apply_to_zone(self, zone: Zone, action_type: str) -> dict:
        simulation = self.simulate(zone, action_type)

        for metric, value in simulation["after_metrics"].items():
            setattr(zone, metric, value)

        zone.urban_quality_index = simulation["after_urban_quality_index"]
        return simulation

    def _build_metric_impacts(self, before_metrics: dict, after_metrics: dict) -> list[MetricImpact]:
        impacts: list[MetricImpact] = []

        for metric in METRIC_FIELDS:
            before_value = round2(before_metrics[metric])
            after_value = round2(after_metrics[metric])
            delta = round2(after_value - before_value)
            if delta != 0:
                impacts.append(
                    MetricImpact(
                        metric=metric,
                        before=before_value,
                        after=after_value,
                        delta=delta,
                    )
                )

        return impacts