import logging

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.priority_alert import PriorityAlert
from app.models.telegram_dispatch_log import TelegramDispatchLog
from app.models.zone import Zone
from app.utils.helpers import now_utc, round2

logger = logging.getLogger(__name__)


class TelegramService:
    def is_enabled(self) -> bool:
        return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)

    def build_alert_key(self, zone_id: int, improvement_type: str, lat: float, lon: float) -> str:
        lat_bucket = round(lat, 3)
        lon_bucket = round(lon, 3)
        return f"{zone_id}:{improvement_type}:{lat_bucket}:{lon_bucket}"

    def is_on_cooldown(self, db: Session, alert_key: str) -> bool:
        log = (
            db.query(TelegramDispatchLog)
            .filter(TelegramDispatchLog.alert_key == alert_key)
            .order_by(TelegramDispatchLog.created_at.desc())
            .first()
        )
        if not log:
            return False

        delta_seconds = (now_utc() - log.created_at).total_seconds()
        return delta_seconds < (settings.TELEGRAM_ALERT_COOLDOWN_MINUTES * 60)

    def format_priority_alert_message(self, alert: PriorityAlert, zone: Zone) -> str:
        return (
            "🚨 Digital Twin City Priority Alert\n\n"
            f"Zone: {zone.name} ({zone.zone_type})\n"
            f"Improvement: {alert.improvement_type}\n"
            f"Priority Score: {round2(alert.priority_score)} / 100\n"
            f"Priority Level: {alert.priority_level.upper()}\n"
            f"AI Beneficial: {'YES' if alert.ai_beneficial else 'NO'}\n"
            f"AI Benefit Score: {round2(alert.ai_benefit_score)}\n"
            f"Confidence: {round2(alert.ai_confidence)}\n"
            f"Exact Zone Matches: {alert.exact_zone_matches_count}\n"
            f"Nearby Similar Requests: {alert.nearby_similar_requests_count}\n"
            f"Unique Nearby Users: {alert.unique_users_nearby_count}\n"
            f"Hotspot Score: {round2(alert.hotspot_score)}\n"
            f"Coordinates: {round(alert.latitude, 6)}, {round(alert.longitude, 6)}\n\n"
            f"Summary: {alert.summary}\n"
            f"Recommended Action: {alert.recommended_action}"
        )

    def send_priority_alert(
        self,
        db: Session,
        alert: PriorityAlert,
        zone: Zone,
    ) -> bool:
        alert_key = self.build_alert_key(alert.zone_id, alert.improvement_type, alert.latitude, alert.longitude)
        message = self.format_priority_alert_message(alert, zone)

        if self.is_on_cooldown(db, alert_key):
            self._log_dispatch(
                db=db,
                alert_key=alert_key,
                improvement_type=alert.improvement_type,
                zone_name=zone.name,
                latitude=alert.latitude,
                longitude=alert.longitude,
                message=message,
                success=False,
                response_text="Skipped بسبب cooldown",
            )
            return False

        if not self.is_enabled():
            self._log_dispatch(
                db=db,
                alert_key=alert_key,
                improvement_type=alert.improvement_type,
                zone_name=zone.name,
                latitude=alert.latitude,
                longitude=alert.longitude,
                message=message,
                success=False,
                response_text="Telegram disabled by configuration",
            )
            return False

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            success = response.ok
            self._log_dispatch(
                db=db,
                alert_key=alert_key,
                improvement_type=alert.improvement_type,
                zone_name=zone.name,
                latitude=alert.latitude,
                longitude=alert.longitude,
                message=message,
                success=success,
                response_text=response.text[:3000],
            )
            return success
        except requests.RequestException as exc:
            logger.exception("Telegram dispatch failed: %s", exc)
            self._log_dispatch(
                db=db,
                alert_key=alert_key,
                improvement_type=alert.improvement_type,
                zone_name=zone.name,
                latitude=alert.latitude,
                longitude=alert.longitude,
                message=message,
                success=False,
                response_text=str(exc),
            )
            return False

    def _log_dispatch(
        self,
        db: Session,
        alert_key: str,
        improvement_type: str,
        zone_name: str,
        latitude: float,
        longitude: float,
        message: str,
        success: bool,
        response_text: str,
    ) -> None:
        log = TelegramDispatchLog(
            alert_key=alert_key,
            improvement_type=improvement_type,
            zone_name=zone_name,
            latitude=latitude,
            longitude=longitude,
            message=message,
            success=success,
            response_text=response_text,
        )
        db.add(log)
        db.commit()