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
    servers = servers_func(session)

    for server in servers:
        # Check server SSH connectivity
        server_online = check_server_ssh(server.ip)

        # Check all services health status
        service_statuses = []
        for service in server.services:
            if service.health_url:
                service_online = check_service_health(service.health_url)
                service_statuses.append(service_online)
            else:
                # Services without health check URL default to online
                service_statuses.append(True)

        # Update server status
        new_status = "online" if server_online else "offline"

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

        # Update each service status
        db_server = session.get(Server, server.id)
        if db_server:
            for i, svc in enumerate(db_server.services):
                if i < len(service_statuses):
                    svc.status = "online" if service_statuses[i] else "offline"

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