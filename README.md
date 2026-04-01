# 5000 信息系统开发部 - 服务器运维管理系统

> 5000信息系统开发部服务器运维管理系统，支持AI智能填充、健康检查和智能问答。

## 功能特性

### 1. 服务器管理
- 添加、编辑、删除服务器
- 服务器状态监控（在线/离线/维护中）
- 支持 SSH 凭证存储

### 2. AI 智能填充
- 自然语言描述服务器信息，AI 自动提取并填充
- 支持提取：IP、用户名、密码、服务名称、健康检查URL等

### 3. 健康检查
- 自动检查服务器 SSH 端口连通性
- 自动检查服务 healthUrl HTTP 状态码（200 = 正常）
- 后台定时检查（每 5 分钟）

### 4. AI 智能问答
- 基于本地 Qwen3 AI 进行智能问答
- 支持查询服务器、服务相关信息
- 自动关联服务器记录和知识库

### 5. 快速录入
- 一步完成：描述 → AI 提取 → 自动保存

## 技术栈

- **后端**: FastAPI + SQLite (SQLModel)
- **前端**: React 19 + TypeScript + Vite + Tailwind CSS
- **AI**: Qwen/Qwen3-30B-A3B-Instruct-2507 (本地部署)

## 快速开始

### 前置要求

- Python 3.13+
- Node.js 22+
- 本地 AI 服务：`http://10.17.150.235:8000/v1`

### 1. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn backend.main:app --reload --port 8889

# 或使用脚本
bash backend/server.sh start
```

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 创建环境配置
echo "VITE_API_BASE_URL=http://127.0.0.1:8889" > .env.local

# 启动开发服务器
npm run dev
```

### 3. 访问系统

打开浏览器访问：http://localhost:5173

## 使用指南

### 添加服务器

两种方式：

1. **普通模式**：点击"添加服务器"按钮，填写完整表单
2. **快速录入**：点击"快速录入"按钮，用自然语言描述服务器信息

#### 快速录入示例

```
192.168.1.100，用户名 root，密码 password123，运行 Nginx 和 Docker 服务
```

AI 会自动提取：
- IP: 192.168.1.100
- 用户名: root
- 密码: password123
- 服务: Nginx, Docker

### AI 助手

点击右下角"AI 助手"按钮，可以：

- 查询服务器信息
- 搜索特定服务
- 了解服务器状态
- 故障排查建议

#### 示例问题

- "有哪些服务器？"
- "Docker 在哪台服务器上？"
- "Nginx 服务健康检查失败怎么办？"

### 健康检查

系统每 5 分钟自动检查：

1. **服务器**：SSH 端口（22）连通性
2. **服务**：healthUrl HTTP 状态码（200 = 在线）

状态会在服务器详情页实时显示。

## 项目结构

```
serverops-memo/
├── backend/                 # FastAPI 后端
│   ├── main.py             # 应用入口
│   ├── models.py           # 数据库模型
│   ├── schemas.py          # Pydantic 模型
│   ├── services.py         # 业务逻辑
│   ├── db.py               # 数据库配置
│   └── serverops.db        # SQLite 数据库
├── frontend/               # React 前端
│   ├── src/
│   │   ├── App.tsx        # 主应用
│   │   ├── components/    # React 组件
│   │   ├── lib/           # API 客户端
│   │   ├── types.ts       # TypeScript 类型
│   │   └── index.css      # 样式
│   └── dist/              # 构建产物
└── docs/                  # 知识库文档
    └── knowledge/         # Markdown 文档
```

## 环境变量

### 后端

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SERVEROPS_DATABASE_URL` | `sqlite:///./serverops.db` | 数据库连接 |
| `SERVEROPS_CORS_ORIGINS` | - | CORS 允许的源 |
| `SERVEROPS_AI_URL` | `http://10.17.150.235:8000/v1` | AI 服务地址 |
| `SERVEROPS_AI_MODEL` | `/models/Qwen/Qwen3-30B-A3B-Instruct-2507` | AI 模型 |

### 前端

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VITE_API_BASE_URL` | `http://127.0.0.1:8889` | API 地址 |

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/servers` | 获取服务器列表 |
| POST | `/api/servers` | 创建服务器 |
| PUT | `/api/servers/{id}` | 更新服务器 |
| DELETE | `/api/servers/{id}` | 删除服务器 |
| POST | `/api/assistant/query` | AI 问答 |
| POST | `/api/ai/extract-server` | AI 提取服务器信息 |

## 常见问题

### Q: 健康检查失败怎么办？

A: 检查以下几点：
1. 服务器 SSH 端口（22）是否开放
2. 服务 healthUrl 是否可访问
3. 网络连通性

### Q: AI 助手回答不准确？

A: 确保：
1. 本地 AI 服务正常运行
2. 服务器信息已正确录入
3. 知识库文档已添加

### Q: 如何查看详细日志？

A: 查看后端日志文件：`backend/.serverops-backend.log`

## 开发相关

### 运行测试

```bash
pytest backend/tests/ -v
```

### 构建生产版本

```bash
cd frontend
npm run build
```

### 代码规范

- 后端遵循 PEP 8
- 前端使用 TypeScript + ESLint
- 使用 Black 格式化 Python 代码
- 使用 Prettier 格式化 JavaScript/TypeScript