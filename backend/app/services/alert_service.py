"""
Alert notification services.
"""
from __future__ import annotations

import logging

import httpx
from sqlmodel import Session, select

from backend.app.config import settings
from backend.app.models import AlertRecord

logger = logging.getLogger(__name__)


def send_alert(
    server_name: str,
    server_ip: str,
    alert_type: str,  # "server" or "service"
    service_name: str | None = None,
    status: str = "offline",
) -> bool:
    """
    Send alert notification to webhook.

    Returns True if alert was sent successfully, False otherwise.
    """
    if not settings.ALERT_ENABLED:
        logger.info("Alert notifications are disabled")
        return False

    # Build alert content
    if alert_type == "server":
        title = f"服务器异常告警: {server_name}"
        content = f"服务器 {server_name} ({server_ip}) 已离线，请检查网络连接和SSH服务。"
    else:
        title = f"服务异常告警: {server_name}"
        content = f"服务器 {server_name} ({server_ip}) 上的服务 {service_name} 已离线，请检查服务状态。"

    payload = {
        "component_name": settings.ALERT_COMPONENT_NAME,
        "itcode": settings.ALERT_ITCODE,
        "content": content,
        "title": title,
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(settings.ALERT_WEBHOOK_URL, json=payload)
            response.raise_for_status()
            logger.info(f"Alert sent successfully: {title}")
            return True
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")
        return False


def should_send_alert(session: Session, server_id: str, service_name: str | None) -> bool:
    """
    Check if alert should be sent (deduplication).

    Returns True if no alert has been sent yet for this server/service.
    """
    statement = select(AlertRecord).where(
        AlertRecord.server_id == server_id,
        AlertRecord.service_name == service_name,
    )
    existing = session.exec(statement).first()
    return existing is None


def record_alert(
    session: Session,
    server_id: str,
    service_name: str | None,
    alert_type: str,
) -> None:
    """Record that an alert has been sent."""
    alert_record = AlertRecord(
        server_id=server_id,
        service_name=service_name,
        alert_type=alert_type,
    )
    session.add(alert_record)
    session.commit()
    logger.info(f"Alert recorded for server_id={server_id}, service={service_name}")