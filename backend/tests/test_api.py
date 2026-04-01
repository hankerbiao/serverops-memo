from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    os.environ["SERVEROPS_DATABASE_URL"] = f"sqlite:///{tmp_path / 'serverops.db'}"
    os.environ.pop("GEMINI_API_KEY", None)

    from backend.main import create_app

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_server_crud_flow(client: TestClient) -> None:
    create_response = client.post(
        "/api/servers",
        json={
            "name": "Production-Web-01",
            "ip": "192.168.1.10",
            "username": "root",
            "password": "secret",
            "sshKey": "",
            "status": "online",
            "tags": [{"name": "生产", "color": "#ef4444"}],
            "aliases": ["prod-web"],
            "notes": "主入口 Web 服务器",
            "services": [
                {
                    "name": "Nginx",
                    "healthUrl": "http://192.168.1.10/health",
                    "category": "web",
                    "aliases": ["edge-proxy"],
                    "notes": "反向代理入口",
                },
                {
                    "name": "Redis",
                    "healthUrl": "",
                    "category": "cache",
                    "aliases": ["session-cache"],
                    "notes": "会话缓存",
                },
            ],
        },
    )

    assert create_response.status_code == 201
    created_server = create_response.json()
    assert created_server["name"] == "Production-Web-01"
    assert created_server["lastChecked"]
    assert created_server["tags"][0]["name"] == "生产"
    assert created_server["aliases"] == ["prod-web"]
    assert created_server["notes"] == "主入口 Web 服务器"
    assert len(created_server["services"]) == 2
    assert all(service["status"] == "online" for service in created_server["services"])
    assert created_server["services"][0]["category"] == "web"
    assert created_server["services"][0]["aliases"] == ["edge-proxy"]
    assert created_server["services"][0]["notes"] == "反向代理入口"

    list_response = client.get("/api/servers")

    assert list_response.status_code == 200
    servers = list_response.json()
    assert len(servers) == 1
    assert servers[0]["id"] == created_server["id"]

    update_response = client.put(
        f"/api/servers/{created_server['id']}",
        json={
            "name": "Production-Web-01",
            "ip": "192.168.1.10",
            "username": "ubuntu",
            "password": "rotated",
            "sshKey": "ops-key",
            "status": "maintenance",
            "tags": [{"name": "AI", "color": "#3b82f6"}],
            "aliases": ["prod-web-legacy"],
            "notes": "正在迁移",
            "services": [
                {
                    "name": "Nginx",
                    "healthUrl": "http://192.168.1.10/health",
                    "status": "checking",
                    "category": "web",
                    "aliases": ["edge-gateway"],
                    "notes": "正在切流",
                }
            ],
        },
    )

    assert update_response.status_code == 200
    updated_server = update_response.json()
    assert updated_server["username"] == "ubuntu"
    assert updated_server["status"] == "maintenance"
    assert updated_server["tags"][0]["name"] == "AI"
    assert updated_server["aliases"] == ["prod-web-legacy"]
    assert updated_server["notes"] == "正在迁移"
    assert updated_server["services"] == [
        {
            "name": "Nginx",
            "healthUrl": "http://192.168.1.10/health",
            "status": "checking",
            "category": "web",
            "aliases": ["edge-gateway"],
            "notes": "正在切流",
        }
    ]

    delete_response = client.delete(f"/api/servers/{created_server['id']}")

    assert delete_response.status_code == 204
    assert client.get("/api/servers").json() == []


def test_delete_cascades_services(client: TestClient) -> None:
    create_response = client.post(
        "/api/servers",
        json={
            "name": "Staging-DB",
            "ip": "10.0.0.5",
            "username": "admin",
            "password": "",
            "sshKey": "",
            "status": "offline",
            "tags": [],
            "aliases": [],
            "notes": "",
            "services": [{
                "name": "PostgreSQL",
                "healthUrl": "http://10.0.0.5/status",
                "category": "database",
                "aliases": [],
                "notes": "",
            }],
        },
    )
    server_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/servers/{server_id}")

    assert delete_response.status_code == 204
    list_response = client.get("/api/servers")
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_chat_endpoint_uses_db_context_and_hides_passwords(client: TestClient) -> None:
    client.post(
        "/api/servers",
        json={
            "name": "Dev-AI-Worker",
            "ip": "192.168.50.12",
            "username": "dev",
            "password": "do-not-return-me",
            "sshKey": "",
            "status": "offline",
            "tags": [{"name": "AI", "color": "#3b82f6"}],
            "aliases": ["gpu-worker"],
            "notes": "本地模型节点",
            "services": [{
                "name": "Ollama",
                "healthUrl": "http://192.168.50.12:11434",
                "category": "ai-runtime",
                "aliases": ["local-llm"],
                "notes": "提供本地推理",
            }],
        },
    )

    response = client.post("/api/chat", json={"message": "Summarize current infrastructure"})

    assert response.status_code == 200
    payload = response.json()
    assert "Dev-AI-Worker" in payload["reply"]
    assert "192.168.50.12" in payload["reply"]
    assert "do-not-return-me" not in payload["reply"]
    assert payload["usedFallback"] is True


def test_tag_crud_and_server_searchable_metadata(client: TestClient) -> None:
    create_tag_response = client.post(
        "/api/tags",
        json={"name": "监控", "color": "#22c55e"},
    )

    assert create_tag_response.status_code == 201
    created_tag = create_tag_response.json()
    assert created_tag["name"] == "监控"

    list_response = client.get("/api/tags")
    assert list_response.status_code == 200
    assert list_response.json() == [created_tag]

    update_response = client.put(
        f"/api/tags/{created_tag['id']}",
        json={"name": "监控告警", "color": "#16a34a"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "监控告警"

    delete_response = client.delete(f"/api/tags/{created_tag['id']}")
    assert delete_response.status_code == 204
    assert client.get("/api/tags").json() == []


def test_assistant_query_combines_asset_records_and_local_knowledge(client: TestClient) -> None:
    client.post(
        "/api/servers",
        json={
            "name": "GPU-Node-01",
            "ip": "10.1.0.8",
            "username": "ops",
            "password": "",
            "sshKey": "",
            "status": "online",
            "tags": [{"name": "AI", "color": "#3b82f6"}],
            "aliases": ["llm-node"],
            "notes": "用于本地模型推理和 Web 界面",
            "services": [
                {
                    "name": "Open WebUI",
                    "healthUrl": "http://10.1.0.8:3000/health",
                    "category": "ai-ui",
                    "aliases": ["webui"],
                    "notes": "提供聊天界面",
                },
                {
                    "name": "Ollama",
                    "healthUrl": "http://10.1.0.8:11434/api/tags",
                    "category": "ai-runtime",
                    "aliases": ["local-model-api"],
                    "notes": "提供本地模型服务",
                },
            ],
        },
    )

    response = client.post(
        "/api/assistant/query",
        json={"message": "帮我找 AI 相关服务，并告诉我 Open WebUI 一般怎么排查"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "summary" in payload["answer"]
    assert payload["answer"]["records"]
    assert payload["answer"]["records"][0]["serverName"] == "GPU-Node-01"
    assert {record["serviceName"] for record in payload["answer"]["records"]} >= {"Open WebUI", "Ollama"}
    assert payload["answer"]["knowledge"]
    assert "Open WebUI" in payload["answer"]["knowledge"][0]["title"]
    assert any("打开" in action for action in payload["answer"]["nextActions"])
