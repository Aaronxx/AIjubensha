# AIjubensha

基于大语言模型的多人在线 AI 剧本杀（Murder Mystery Game）平台：由 AI 扮演剧本中的 NPC 角色，玩家在房间内联机进行剧情对话、搜证、投票与结算。

## 功能特性

- 🎭 **AI NPC 引擎**：LLM 驱动的 NPC 角色扮演，支持主/备模型自动切换、重试与超时控制，内置剧本校验与 NPC 状态管理
- 🏠 **房间系统**：创建/加入房间，WebSocket 实时联机
- 📜 **剧本管理**：剧本、角色、剧情推进（dialogue / investigation / voting / settlement）
- 🔐 **用户系统**：JWT 认证（注册/登录）
- 🛒 **商店系统**：游戏内道具/角色商店
- 🛠 **管理后台**：独立后台服务，提供仪表盘、剧本与角色管理接口

## 项目结构

```
AIjubensha/
├── game-server/       # 玩家端后端（FastAPI + WebSocket + PostgreSQL + Redis）
├── admin-server/      # 管理后台服务（FastAPI，独立端口）
├── ai-npc-engine/     # AI NPC 引擎（LLM 客户端、NPC 工厂、剧本校验）
├── flutter-client/    # Flutter 跨平台客户端（Android / iOS / 桌面 / Web）
├── ios-client/        # 原生 iOS 客户端（Xcode 工程）
├── web-app/           # Web 页面原型
├── docker-compose.yml # 本地基础设施（PostgreSQL 16 + Redis 7 + game-server）
└── codemagic.yaml     # iOS 构建流水线（Codemagic CI）
```

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python · FastAPI · SQLAlchemy 2 (asyncpg) · WebSockets |
| 数据 | PostgreSQL 16 · Redis 7 |
| 认证 | JWT（python-jose + passlib） |
| AI | DeepSeek API（`deepseek-chat`，支持自定义 fallback 模型） |
| 客户端 | Flutter（provider 状态管理）· Swift / Xcode |
| 基础设施 | Docker Compose · Codemagic CI |

## 快速开始

### 前置要求

- Python 3.10+
- Docker & Docker Compose（或自备 PostgreSQL / Redis）
- Flutter SDK（运行客户端）
- [DeepSeek API Key](https://platform.deepseek.com/)

### 1. 启动基础设施

```bash
docker compose up -d postgres redis
```

### 2. 配置环境变量

```bash
cp game-server/.env.example game-server/.env
# 编辑 .env，填入 DEEPSEEK_API_KEY
```

### 3. 启动玩家端后端（端口 8000）

```bash
cd game-server
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
# API 文档：http://localhost:8000/docs
```

### 4. 启动管理后台（端口 8001）

```bash
cd admin-server
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
# 后台 API 文档：http://localhost:8001/docs
```

### 5. 运行 Flutter 客户端

```bash
cd flutter-client
flutter pub get
flutter run
```

也可以用 Docker Compose 一键启动完整后端：

```bash
cp .env.example .env   # 填入 DEEPSEEK_API_KEY
docker compose up --build
```

## 开发

```bash
cd game-server
pip install -r requirements.txt
pytest
```

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE).

Required Notice: Copyright (c) 2026 Aaronxx

Personal study, research, hobby, and other noncommercial use is permitted. **Commercial use requires a separate license from the author.**
