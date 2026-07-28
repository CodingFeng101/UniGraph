# 部署文档

本文档覆盖两种部署方式：

- 传统部署：前端、后端、Celery、MySQL、Redis 分开部署
- Docker 部署：通过 `docker compose` 启动整套服务

## 1. 项目组成

- `frontend`：Vue 3 + Vite 前端
- `backend`：FastAPI 后端
- `celery`：异步任务 worker
- `mysql`：业务数据库
- `redis`：缓存与任务队列

## 2. 基础要求

建议环境：

- Python 3.11
- Node.js 20+
- MySQL 8.x
- Redis 7.x
- Docker 24+ 与 Docker Compose v2（仅 Docker 部署需要）

数据库初始化：

```sql
CREATE DATABASE onlineunigraph CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

导入初始化数据：

```bash
mysql -uroot -p onlineunigraph < deploy/mysql/init/01-schema.sql
```

## 3. 传统部署

### 3.1 后端配置

复制环境变量模板：

```bash
cp backend/.env.template backend/.env
```

按实际环境修改：

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`
- `REDIS_HOST`
- `REDIS_PORT`
- `OPENAI_API_KEY`
- `EMBEDDING_MODEL`
- `TOKEN_SECRET_KEY`
- `OPERA_LOG_ENCRYPT_SECRET_KEY`
- `CORS_ALLOWED_ORIGINS`（JSON 数组，例如 `["http://localhost:5173"]`）

### 3.2 后端启动

Linux / macOS：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Windows PowerShell：

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

接口地址：

- OpenAPI 文档：`http://localhost:8000/knowg/v1/docs`
- OpenAPI JSON：`http://localhost:8000/knowg/v1/openapi`

### 3.3 Celery 启动

Linux / macOS：

```bash
celery -A backend.app.task.celery:celery_app worker --loglevel=info
```

Windows：

```powershell
celery -A backend.app.task.celery:celery_app worker --pool=solo --loglevel=info
```

如果你希望 Windows 上同时跑多个任务，可以再额外开几个 worker 窗口。

### 3.4 前端启动

开发模式：

```bash
cd frontend
npm ci
npm run dev
```

生产构建：

```bash
cd frontend
npm ci
npm run build
```

前端运行时配置来自 `frontend/public/config.js`。

静态部署时可在 `config.js` 里覆盖：

```js
window.FRONTEND_CONFIG = {
  VITE_HOST_URL: '',
  VITE_API_BASE_URL: '/knowg',
  VITE_SHOW_IMAGE_API: '/knowg/v1/image/',
  VITE_USER_INFO_SSO_URL: '/knowg/v1/sys/users/me',
};
```

### 3.5 推荐端口

- 前端：`8080`
- 后端：`8000`
- MySQL：`3306`
- Redis：`6379`

### 3.6 Nginx 反向代理

可参考：

- `deploy/nginx/default.conf.template`

核心思路：

- `/` 提供前端静态资源
- `/knowg/` 反向代理到后端 `8000`

## 4. Docker 部署

### 4.1 配置环境变量

复制模板：

```bash
cp .env.docker.example .env.docker
```

至少修改这些值：

- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`
- `TOKEN_SECRET_KEY`
- `OPERA_LOG_ENCRYPT_SECRET_KEY`
- `OPENAI_API_KEY`
- `CORS_ALLOWED_ORIGINS`
- `FRONTEND_PORT`
- `BACKEND_PORT`

### 4.2 开发或单机部署

```bash
docker compose --env-file .env.docker up -d --build
```

### 4.3 生产部署

```bash
docker compose --env-file .env.docker -f compose.yaml -f deploy/compose.prod.yaml up -d --build
```

### 4.4 服务说明

- `frontend`：Nginx 托管前端并代理 `/knowg/`
- `backend`：FastAPI
- `celery`：Celery worker
- `mysql`：MySQL 8.4
- `redis`：Redis 7

默认访问地址：

- 前端：`http://localhost:8080`
- 后端文档：`http://localhost:8000/knowg/v1/docs`

### 4.5 常用命令

查看全部日志：

```bash
docker compose --env-file .env.docker logs -f
```

查看单个服务日志：

```bash
docker compose --env-file .env.docker logs -f backend
docker compose --env-file .env.docker logs -f celery
docker compose --env-file .env.docker logs -f frontend
```

停止服务：

```bash
docker compose --env-file .env.docker down
```

连同数据卷一起删除：

```bash
docker compose --env-file .env.docker down -v
```

## 5. 持久化目录

这些目录或卷建议保留：

- `backend/static`
- `var`
- `mysql_data`
- `redis_data`

## 6. 部署相关文件

- `compose.yaml`
- `deploy/compose.prod.yaml`
- `deploy/docker/backend.Dockerfile`
- `deploy/docker/frontend.Dockerfile`
- `deploy/mysql/init/01-schema.sql`
- `deploy/nginx/default.conf.template`
- `deploy/nginx/40-runtime-config.sh`
- `frontend/public/config.js`
- `.env.docker.example`
- `.dockerignore`
- `.gitignore`
- `backend/.env.template`

## 7. Ignore 建议

当前已经把常见运行产物加入忽略规则，重点包括：

- Python 虚拟环境与缓存
- 前端 `node_modules` 与 `dist`
- 本地日志目录
- 后端静态上传目录与临时目录
- Docker 本地环境文件

如果你后续新增了本地运行目录，也建议同步加入 `.gitignore` 或 `.dockerignore`。
