from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Digital Twin City Backend"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./digital_twin_city.db"
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    PRIORITY_ALERT_THRESHOLD: float = 72.0
    HOTSPOT_RADIUS_METERS: float = 300.0
    TELEGRAM_ALERT_COOLDOWN_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()