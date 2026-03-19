from app.db.base import Base
from app.db.session import engine
from app.models import (
    ChatMessage,
    PlacedImprovement,
    PriorityAlert,
    SimulationHistory,
    Suggestion,
    TelegramDispatchLog,
    User,
    Zone,
)


def init_db() -> None:
    _ = (
        Zone,
        User,
        ChatMessage,
        Suggestion,
        SimulationHistory,
        PriorityAlert,
        TelegramDispatchLog,
        PlacedImprovement,
    )
    Base.metadata.create_all(bind=engine)
