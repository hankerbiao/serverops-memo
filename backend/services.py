from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlmodel import Session, select

from backend.models import Server, Service, Tag
from backend.schemas import (
    AssistantAnswer,
    AssistantKnowledge,
    AssistantRecord,
    ExtractedServerInfo,
    ExtractedService,
    ServerRead,
    ServerWrite,
    TagRead,
    TagWrite,
)


def format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_tag_read(tag: Tag) -> TagRead:
    return TagRead(id=tag.id, name=tag.name, color=tag.color)


def to_server_read(server: Server) -> ServerRead:
    return ServerRead(
        id=server.id,
        name=server.name,
        ip=server.ip,
        username=server.username,
        password=server.password,
        sshKey=server.ssh_key,
        status=server.status,
        lastChecked=format_timestamp(server.last_checked),
        tags=[to_tag_read(tag) for tag in server.tags],
        aliases=list(server.aliases or []),
        notes=server.notes,
        services=[
            {
                "name": service.name,
                "healthUrl": service.health_url,
                "status": service.status,
                "category": service.category,
                "aliases": list(service.aliases or []),
                "notes": service.notes,
            }
            for service in server.services
        ],
    )


def list_servers(session: Session) -> list[ServerRead]:
    statement = select(Server).order_by(Server.last_checked.desc())
    servers = session.exec(statement).unique().all()
    return [to_server_read(server) for server in servers]


def list_tags(session: Session) -> list[TagRead]:
    statement = select(Tag).order_by(Tag.name.asc())
    tags = session.exec(statement).all()
    return [to_tag_read(tag) for tag in tags]


def _resolve_tags(session: Session, payload_tags: list[TagWrite]) -> list[Tag]:
    resolved: list[Tag] = []
    for payload_tag in payload_tags:
        tag = None
        if payload_tag.id:
            tag = session.get(Tag, payload_tag.id)
        if tag is None:
            statement = select(Tag).where(Tag.name == payload_tag.name)
            tag = session.exec(statement).first()
        if tag is None:
            tag = Tag(
                id=payload_tag.id or uuid4().hex,
                name=payload_tag.name,
                color=payload_tag.color,
            )
            session.add(tag)
            session.flush()
        else:
            tag.name = payload_tag.name
            tag.color = payload_tag.color
            session.add(tag)
        resolved.append(tag)
    return resolved


def create_tag(session: Session, payload: TagWrite) -> TagRead:
    tag = Tag(id=payload.id or uuid4().hex, name=payload.name, color=payload.color)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return to_tag_read(tag)


def update_tag(session: Session, tag_id: str, payload: TagWrite) -> TagRead | None:
    tag = session.get(Tag, tag_id)
    if tag is None:
        return None
    tag.name = payload.name
    tag.color = payload.color
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return to_tag_read(tag)


def delete_tag(session: Session, tag_id: str) -> bool:
    tag = session.get(Tag, tag_id)
    if tag is None:
        return False
    session.delete(tag)
    session.commit()
    return True


def create_server(session: Session, payload: ServerWrite) -> ServerRead:
    server = Server(
        id=uuid4().hex,
        name=payload.name,
        ip=payload.ip,
        username=payload.username,
        password=payload.password or None,
        ssh_key=payload.ssh_key or None,
        status=payload.status,
        aliases=list(payload.aliases),
        notes=payload.notes or None,
        last_checked=datetime.now(timezone.utc),
        services=[
            Service(
                name=service.name,
                health_url=service.health_url or None,
                status=service.status or "online",
                category=service.category or None,
                aliases=list(service.aliases),
                notes=service.notes or None,
            )
            for service in payload.services
        ],
        tags=_resolve_tags(session, payload.tags),
    )
    session.add(server)
    session.commit()
    session.refresh(server)
    return to_server_read(server)


def update_server(session: Session, server_id: str, payload: ServerWrite) -> ServerRead | None:
    server = session.get(Server, server_id)
    if server is None:
        return None

    server.name = payload.name
    server.ip = payload.ip
    server.username = payload.username
    server.password = payload.password or None
    server.ssh_key = payload.ssh_key or None
    server.status = payload.status
    server.aliases = list(payload.aliases)
    server.notes = payload.notes or None
    server.last_checked = datetime.now(timezone.utc)
    server.tags = _resolve_tags(session, payload.tags)

    server.services.clear()
    for service in payload.services:
        server.services.append(
            Service(
                name=service.name,
                health_url=service.health_url or None,
                status=service.status or "online",
                category=service.category or None,
                aliases=list(service.aliases),
                notes=service.notes or None,
                server_id=server.id,
            )
        )

    session.add(server)
    session.commit()
    session.refresh(server)
    return to_server_read(server)


def delete_server(session: Session, server_id: str) -> bool:
    server = session.get(Server, server_id)
    if server is None:
        return False

    session.delete(server)
    session.commit()
    return True


def build_chat_context(servers: list[ServerRead]) -> str:
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
    context = build_chat_context(servers)
    return (
        "ServerOps summary\n\n"
        f"Question: {message}\n\n"
        "Current infrastructure:\n"
        f"{context}"
    )


def generate_chat_reply(message: str, servers: list[ServerRead]) -> tuple[str, bool]:
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
    """使用本地 AI 从描述中提取服务器信息"""
    import httpx
    import json
    import re

    ai_url = os.getenv("SERVEROPS_AI_URL", "http://10.17.150.235:8000/v1")
    ai_model = os.getenv("SERVEROPS_AI_MODEL", "/models/Qwen/Qwen3-30B-A3B-Instruct-2507")

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

            # 尝试解析 JSON
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

    # 失败时返回空对象
    return ExtractedServerInfo()


def _normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def _knowledge_root() -> Path:
    return Path(__file__).resolve().parent.parent / "docs" / "knowledge"


def _message_keywords(message: str) -> list[str]:
    keywords = {_normalize_text(part) for part in message.replace("，", " ").replace(",", " ").split()}
    extra = set()
    lowered = _normalize_text(message)
    if "ai" in lowered:
        extra.update({"ai", "ollama", "open webui", "open-webui"})
    if "open webui" in lowered or "open-webui" in lowered:
        extra.update({"open webui", "open-webui", "webui"})
    return [keyword for keyword in keywords.union(extra) if keyword]


def _score_server(message: str, server: ServerRead) -> int:
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
    actions: list[str] = []
    if records:
        actions.append(f"打开 {records[0].server_name} 详情")
        if records[0].health_url:
            actions.append(f"检查 {records[0].service_name} 的健康检查地址")
    if knowledge:
        actions.append(f"查看 {knowledge[0].title} 文档")
    return actions


def generate_assistant_answer(message: str, servers: list[ServerRead]) -> AssistantAnswer:
    # 首先尝试使用本地 AI
    try:
        import httpx
        import json
        import re

        ai_url = os.getenv("SERVEROPS_AI_URL", "http://10.17.150.235:8000/v1")
        ai_model = os.getenv("SERVEROPS_AI_MODEL", "/models/Qwen/Qwen3-30B-A3B-Instruct-2507")

        # 构建服务器上下文
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

            # 从 AI 回复中提取关键信息用于后续操作
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


# Health Check Functions

def check_service_health(health_url: str) -> bool:
    """检查服务健康状态 - HTTP 200 表示正常"""
    import httpx
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(health_url)
            return response.status_code == 200
    except Exception:
        return False


def check_server_ssh(ip: str, port: int = 22) -> bool:
    """检查服务器 SSH 端口是否可连接"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def run_health_checks(session: Session):
    """执行所有服务器和服务的健康检查"""
    from sqlmodel import update

    servers = list_servers(session)

    for server in servers:
        # 检查服务器 SSH 连接
        server_online = check_server_ssh(server.ip)

        # 检查所有服务的健康状态
        service_statuses = []
        for service in server.services:
            if service.health_url:
                service_online = check_service_health(service.health_url)
                service_statuses.append(service_online)
            else:
                # 没有健康检查URL的服务，默认在线
                service_statuses.append(True)

        # 更新服务器状态
        new_status = "online" if server_online else "offline"

        # 更新服务状态
        stmt = (
            update(Server)
            .where(Server.id == server.id)
            .values(
                status=new_status,
                last_checked=datetime.now(timezone.utc),
            )
        )
        session.exec(stmt)

        # 更新每个服务的状态
        db_server = session.get(Server, server.id)
        if db_server:
            for i, svc in enumerate(db_server.services):
                if i < len(service_statuses):
                    svc.status = "online" if service_statuses[i] else "offline"

        session.commit()

    print(f"Health check completed at {datetime.now(timezone.utc).isoformat()}")


def start_health_check_scheduler(session_factory, interval_seconds: int = 300):
    """启动健康检查调度器"""
    import threading
    import time

    def scheduler():
        while True:
            try:
                session = session_factory()
                try:
                    run_health_checks(session)
                finally:
                    session.close()
            except Exception as e:
                print(f"Health check error: {e}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=scheduler, daemon=True)
    thread.start()
    print(f"Health check scheduler started (interval: {interval_seconds}s)")
    return thread
