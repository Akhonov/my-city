from app.db.base import Base
from app.db.session import engine
from app.models import (
    PlacedImprovement,
    PriorityAlert,
    SimulationHistory,
    Suggestion,
    TelegramDispatchLog,
    Zone,
)


def init_db() -> None:
    _ = (
        Zone,
        Suggestion,
        SimulationHistory,
        PriorityAlert,
        TelegramDispatchLog,
        PlacedImprovement,
    )
    Base.metadata.create_all(bind=engine)