import json
from datetime import datetime, timezone
from typing import Any


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def round2(value: float) -> float:
    return round(float(value), 2)


def normalize_signal(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0.0
    return clamp((value / max_value) * 100.0, 0.0, 100.0)


def dumps_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def loads_json(value: str | None, default: Any = None) -> Any:
    if not value:
        return [] if default is None else default
    return json.loads(value)


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)