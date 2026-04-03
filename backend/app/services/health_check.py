"""
Health check services.
"""
from __future__ import annotations

import socket
import threading
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import httpx
from sqlmodel import Session, update

from backend.app.config import settings
from backend.app.models import Server

if TYPE_CHECKING:
    from backend.app.services.server_service import list_servers


def check_service_health(health_url: str) -> bool:
    """Check service health status - HTTP 200 means healthy."""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(health_url)
            return response.status_code == 200
    except Exception:
        return False


def check_server_ssh(ip: str, port: int = 22) -> bool:
    """Check if server SSH port is reachable."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def run_health_checks(session: Session, servers_func: callable) -> None:
    """Execute health checks for all servers and services."""
    # Import here to avoid circular imports
    from backend.app.services.alert_service import record_alert, send_alert, should_send_alert

    servers = servers_func(session)

    for server in servers:
        # Check all services health status
        service_statuses = []
        for service in server.services:
            if service.health_url:
                service_online = check_service_health(service.health_url)
                service_statuses.append(service_online)
            else:
                # Services without health check URL default to online
                service_statuses.append(True)

        # Server is online if at least one service is online
        server_online = any(service_statuses) if service_statuses else False
        new_status = "online" if server_online else "offline"

        # Check for server status change -> send alert if needed
        old_status = server.status
        if old_status == "online" and new_status == "offline":
            if should_send_alert(session, server.id, None):
                send_alert(server.name, server.ip, "server", None, "offline")
                record_alert(session, server.id, None, "server")

        # Update server in database
        stmt = (
            update(Server)
            .where(Server.id == server.id)
            .values(
                status=new_status,
                last_checked=datetime.now(timezone.utc),
            )
        )
        session.exec(stmt)

        # Update each service status and check for alerts
        db_server = session.get(Server, server.id)
        if db_server:
            for i, svc in enumerate(db_server.services):
                old_service_status = svc.status
                new_service_status = "online" if service_statuses[i] else "offline"

                # Update status
                svc.status = new_service_status

                # Check for service status change -> send alert if needed
                if old_service_status == "online" and new_service_status == "offline":
                    if should_send_alert(session, server.id, svc.name):
                        send_alert(server.name, server.ip, "service", svc.name, "offline")
                        record_alert(session, server.id, svc.name, "service")

        session.commit()

    print(f"Health check completed at {datetime.now(timezone.utc).isoformat()}")


def start_health_check_scheduler(session_factory, interval_seconds: int | None = None) -> threading.Thread:
    """Start the health check scheduler."""
    if interval_seconds is None:
        interval_seconds = settings.HEALTH_CHECK_INTERVAL

    def scheduler():
        while True:
            try:
                session = session_factory()
                try:
                    # Import here to avoid circular imports
                    from backend.app.services.server_service import list_servers
                    run_health_checks(session, list_servers)
                finally:
                    session.close()
            except Exception as e:
                print(f"Health check error: {e}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=scheduler, daemon=True)
    thread.start()
    print(f"Health check scheduler started (interval: {interval_seconds}s)")
    return thread