# 5000 信息系统开发部 - 服务器运维管理系统

## 📝 描述

5000信息系统开发部服务器运维管理系统是一款专为企业内部服务器集群管理设计的轻量级运维工具。系统支持 AI 智能填充服务器信息、自动健康检查和智能问答功能，大大简化了服务器运维工作。

### 核心特性

- **🤖 AI 智能填充**: 使用自然语言描述服务器信息，AI 自动提取 IP、用户名、密码、服务等关键字段
- **💚 自动健康检查**: 每5分钟自动检查服务器 SSH 连通性和服务健康状态
- **💬 智能问答助手**: 基于本地大模型提供智能运维问答
- **⚡ 快速录入**: 一步完成描述 → AI 提取 → 自动保存

### 适用场景

- 企业内部服务器集群管理
- 开发/测试环境服务器监控
- 多服务多实例运维场景
- 故障排查和状态监控

---

## 🛠 技术栈

**后端**
- FastAPI - 高性能 Python Web 框架
- SQLModel - Python ORM
- SQLite - 轻量级数据库
- httpx - 异步 HTTP 客户端

**前端**
- React 19 - UI 框架
- TypeScript - 类型安全
- Vite - 构建工具
- Tailwind CSS - 样式框架
- Motion - 动画库

**AI**
- Qwen/Qwen3-30B-A3B-Instruct-2507 - 本地部署大模型

---

## 🚀 快速开始

### 环境要求

- Python 3.13+
- Node.js 22+
- 本地 AI 服务 (`http://10.17.150.235:8000/v1`)

### 安装部署

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/serverops-memo.git
cd serverops-memo

# 2. 启动后端
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8889

# 3. 启动前端
cd ../frontend
npm install
echo "VITE_API_BASE_URL=http://127.0.0.1:8889" > .env.local
npm run dev
```

访问 http://localhost:5173

---

## 📖 使用指南

### 添加服务器

**方式一：快速录入**
1. 点击"快速录入"按钮
2. 输入服务器描述，如：`192.168.1.100，用户名 root，密码 password123，运行 Nginx`
3. 点击"提取并保存"

**方式二：手动添加**
1. 点击"添加服务器"按钮
2. 填写完整表单信息

### AI 助手

点击右下角 AI 助手图标，可进行：
- 查询服务器/服务信息
- 搜索特定服务
- 获取故障排查建议

示例问题：
- "有哪些服务器？"
- "Docker 在哪台服务器上？"
- "Nginx 服务健康检查失败怎么办？"

---

## 📁 项目结构

```
serverops-memo/
├── backend/                 # FastAPI 后端
│   ├── main.py            # 应用入口
│   ├── models.py          # 数据库模型
│   ├── schemas.py         # Pydantic 模型
│   ├── services.py        # 业务逻辑
│   └── db.py              # 数据库配置
├── frontend/               # React 前端
│   ├── src/
│   │   ├── App.tsx       # 主应用
│   │   ├── components/    # React 组件
│   │   ├── lib/           # API 客户端
│   │   └── types.ts       # TypeScript 类型
│   └── dist/              # 构建产物
├── docs/                   # 知识库文档
├── README.md               # 项目文档
└── .gitignore             # Git 忽略配置
```

---

## 🔧 配置说明

### 后端环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SERVEROPS_DATABASE_URL` | `sqlite:///./serverops.db` | 数据库连接 |
| `SERVEROPS_AI_URL` | `http://10.17.150.235:8000/v1` | AI 服务地址 |
| `SERVEROPS_AI_MODEL` | `/models/Qwen/Qwen3-30B-A3B-Instruct-2507` | AI 模型 |

### 前端环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VITE_API_BASE_URL` | `http://127.0.0.1:8889` | API 地址 |

---

## 📋 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/servers` | 获取服务器列表 |
| POST | `/api/servers` | 创建服务器 |
| PUT | `/api/servers/{id}` | 更新服务器 |
| DELETE | `/api/servers/{id}` | 删除服务器 |
| POST | `/api/assistant/query` | AI 问答 |
| POST | `/api/ai/extract-server` | AI 提取服务器信息 |

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 👤 维护者

5000 信息系统开发部