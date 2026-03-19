from pydantic import BaseModel


class DemandAnalyticsResponse(BaseModel):
    totals_by_improvement: list[dict]
    totals_by_zone: list[dict]
    hotspot_suggestions_count: int
    total_suggestions: int


class BenefitAnalyticsResponse(BaseModel):
    average_benefit_score_by_improvement: list[dict]
    average_priority_score_by_improvement: list[dict]
    beneficial_share_by_improvement: list[dict]
    average_zone_need_score_by_improvement: list[dict]