"""
Chat and AI services.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

from backend.app.config import settings
from backend.app.schemas.chat import (
    AssistantAnswer,
    AssistantKnowledge,
    AssistantRecord,
    ExtractedServerInfo,
    ExtractedService,
)
from backend.app.schemas.server import ServerRead

if TYPE_CHECKING:
    from backend.app.services.server_service import list_servers


def build_chat_context(servers: list[ServerRead]) -> str:
    """Build context string from servers."""
    if not servers:
        return "No servers are currently stored."

    lines: list[str] = []
    for server in servers:
        tags = ", ".join(tag.name for tag in server.tags) or "no tags"
        services = ", ".join(
            f"{service.name} ({service.status})" for service in server.services
        ) or "No services"
        lines.append(
            f"- {server.name} [{server.status}] {server.ip} user={server.username}; tags: {tags}; services: {services}"
        )
    return "\n".join(lines)


def fallback_chat_reply(message: str, servers: list[ServerRead]) -> str:
    """Generate fallback reply when AI is unavailable."""
    context = build_chat_context(servers)
    return (
        "ServerOps summary\n\n"
        f"Question: {message}\n\n"
        "Current infrastructure:\n"
        f"{context}"
    )


def generate_chat_reply(message: str, servers: list[ServerRead]) -> tuple[str, bool]:
    """Generate chat reply using Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback_chat_reply(message, servers), True

    try:
        from google import genai
    except ImportError:
        return fallback_chat_reply(message, servers), True

    client = genai.Client(api_key=api_key)
    prompt = (
        "You are a ServerOps Assistant. Answer based only on the following infrastructure data.\n"
        "Do not reveal any passwords.\n\n"
        f"{build_chat_context(servers)}\n\n"
        f"User question: {message}"
    )
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    reply = getattr(response, "text", None) or fallback_chat_reply(message, servers)
    return reply, False


def extract_server_info(description: str) -> ExtractedServerInfo:
    """Extract server info from natural language description using local AI."""
    ai_url = settings.AI_URL
    ai_model = settings.AI_MODEL

    prompt = f"""你是一个服务器信息提取助手。从用户的描述中提取服务器信息，返回 JSON 格式。

只返回纯 JSON，不要其他内容。格式如下:
{{
    "ip": "服务器 IP 地址",
    "username": "SSH 用户名",
    "password": "密码(如果提供)",
    "aliases": ["别名1", "别名2"],
    "notes": "备注说明",
    "services": [
        {{"name": "服务名称", "health_url": "健康检查URL(如果有)", "notes": "服务备注"}}
    ]
}}

如果某字段没有信息，使用 null。不要编造信息。

用户描述: {description}"""

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{ai_url}/chat/completions",
                json={
                    "model": ai_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]

            # Try to parse JSON
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
                return ExtractedServerInfo(
                    ip=data.get("ip"),
                    username=data.get("username"),
                    password=data.get("password"),
                    aliases=data.get("aliases") or [],
                    notes=data.get("notes"),
                    services=[
                        ExtractedService(
                            name=s.get("name", ""),
                            health_url=s.get("health_url"),
                            notes=s.get("notes"),
                        )
                        for s in (data.get("services") or [])
                    ],
                )
    except Exception as e:
        print(f"AI extraction failed: {e}")

    # Return empty on failure
    return ExtractedServerInfo()


def _normalize_text(value: str | None) -> str:
    """Normalize text for search."""
    return (value or "").strip().lower()


def _knowledge_root() -> Path:
    """Get knowledge base root directory."""
    return Path(__file__).resolve().parent.parent.parent.parent / "docs" / "knowledge"


def _message_keywords(message: str) -> list[str]:
    """Extract keywords from message."""
    keywords = {_normalize_text(part) for part in message.replace("，", " ").replace(",", " ").split()}
    extra = set()
    lowered = _normalize_text(message)
    if "ai" in lowered:
        extra.update({"ai", "ollama", "open webui", "open-webui"})
    if "open webui" in lowered or "open-webui" in lowered:
        extra.update({"open webui", "open-webui", "webui"})
    return [keyword for keyword in keywords.union(extra) if keyword]


def _score_server(message: str, server: ServerRead) -> int:
    """Score server relevance to message."""
    haystacks = [
        _normalize_text(server.name),
        _normalize_text(server.ip),
        _normalize_text(server.notes),
        " ".join(_normalize_text(alias) for alias in server.aliases),
        " ".join(_normalize_text(tag.name) for tag in server.tags),
    ]
    for service in server.services:
        haystacks.extend(
            [
                _normalize_text(service.name),
                _normalize_text(service.category),
                _normalize_text(service.notes),
                _normalize_text(service.health_url),
                " ".join(_normalize_text(alias) for alias in service.aliases),
            ]
        )
    joined = "\n".join(haystacks)
    score = 0
    for keyword in _message_keywords(message):
        if keyword and keyword in joined:
            score += 1
    return score


def search_asset_records(message: str, servers: list[ServerRead]) -> list[AssistantRecord]:
    """Search for asset records matching the message."""
    records: list[tuple[int, AssistantRecord]] = []
    for server in servers:
        server_score = _score_server(message, server)
        if server_score <= 0:
            continue
        for service in server.services:
            service_text = " ".join(
                [
                    _normalize_text(service.name),
                    _normalize_text(service.category),
                    _normalize_text(service.notes),
                    _normalize_text(service.health_url),
                    " ".join(_normalize_text(alias) for alias in service.aliases),
                    " ".join(_normalize_text(tag.name) for tag in server.tags),
                    _normalize_text(server.notes),
                ]
            )
            service_score = sum(1 for keyword in _message_keywords(message) if keyword in service_text)
            if service_score > 0:
                records.append(
                    (
                        service_score + server_score,
                        AssistantRecord(
                            type="service",
                            serverId=server.id,
                            serverName=server.name,
                            serviceName=service.name,
                            status=service.status,
                            healthUrl=service.health_url,
                            notes=service.notes or server.notes,
                        ),
                    )
                )
        if not server.services:
            records.append(
                (
                    server_score,
                    AssistantRecord(
                        type="server",
                        serverId=server.id,
                        serverName=server.name,
                        serviceName=None,
                        status=server.status,
                        healthUrl=None,
                        notes=server.notes,
                    ),
                )
            )
    records.sort(key=lambda item: (-item[0], item[1].server_name, item[1].service_name or ""))
    return [record for _, record in records[:5]]


def search_knowledge(message: str) -> list[AssistantKnowledge]:
    """Search knowledge base for matching documents."""
    root = _knowledge_root()
    if not root.exists():
        return []

    matches: list[tuple[int, AssistantKnowledge]] = []
    keywords = _message_keywords(message)
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        haystack = _normalize_text(path.stem.replace("-", " ")) + "\n" + _normalize_text(text)
        score = sum(1 for keyword in keywords if keyword in haystack)
        if score <= 0:
            continue
        lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
        snippet = lines[0] if lines else text.strip()[:120]
        title_line = next((line.strip("# ").strip() for line in text.splitlines() if line.startswith("#")), None)
        matches.append((score, AssistantKnowledge(title=title_line or path.stem.replace("-", " "), snippet=snippet)))

    matches.sort(key=lambda item: (-item[0], item[1].title))
    return [knowledge for _, knowledge in matches[:3]]


def build_next_actions(records: list[AssistantRecord], knowledge: list[AssistantKnowledge]) -> list[str]:
    """Build suggested next actions."""
    actions: list[str] = []
    if records:
        actions.append(f"打开 {records[0].server_name} 详情")
        if records[0].health_url:
            actions.append(f"检查 {records[0].service_name} 的健康检查地址")
    if knowledge:
        actions.append(f"查看 {knowledge[0].title} 文档")
    return actions


def generate_assistant_answer(message: str, servers: list[ServerRead]) -> AssistantAnswer:
    """Generate assistant answer using local AI."""
    ai_url = settings.AI_URL
    ai_model = settings.AI_MODEL

    # First try local AI
    try:
        context = build_chat_context(servers)

        prompt = f"""你是一个服务器运维助手。请根据以下基础设施信息回答用户的问题。

{context}

用户问题: {message}

请用中文回答。如果涉及密码，不要透露具体密码。"""

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{ai_url}/chat/completions",
                json={
                    "model": ai_model,
                    "messages": [
                        {"role": "system", "content": "你是一个服务器运维助手，请用中文回答用户关于基础设施的问题。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            ai_reply = response.json()["choices"][0]["message"]["content"]

            # Extract relevant info from AI reply
            records = search_asset_records(message, servers)
            knowledge = search_knowledge(message)
            next_actions = build_next_actions(records, knowledge)

            return AssistantAnswer(
                summary=ai_reply,
                records=records,
                knowledge=knowledge,
                nextActions=next_actions,
            )
    except Exception as e:
        print(f"AI assistant failed: {e}, falling back to keyword matching")

    # Fallback to keyword matching
    records = search_asset_records(message, servers)
    knowledge = search_knowledge(message)

    summary_parts: list[str] = []
    if records:
        summary_parts.append(f"已找到 {len(records)} 条相关记录")
    else:
        summary_parts.append("未找到直接匹配的系统记录")
    if knowledge:
        summary_parts.append(f"补充了 {len(knowledge)} 条本地知识")

    return AssistantAnswer(
        summary="，".join(summary_parts) + "。",
        records=records,
        knowledge=knowledge,
        nextActions=build_next_actions(records, knowledge),
    )