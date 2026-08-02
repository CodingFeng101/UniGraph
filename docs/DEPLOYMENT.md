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
- `AUTH_AES_SECRET_KEY`（Base64 编码的 32 字节随机值，前端 `VITE_AUTH_AES_SECRET_KEY` 必须使用同一值）
- `LLM_API_KEY_ENCRYPTION_KEY`（模型 API Key 的数据库加密密钥，请独立备份）
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
  VITE_AUTH_AES_SECRET_KEY: '与后端 AUTH_AES_SECRET_KEY 相同的值',
};
```

### 3.5 推荐端口

- 前端：`8080`
- 后端：`8000`
- MySQL：`3306`
- Redis：`6379`

### 3.6 Nginx 反向代理

生产配置示例：

- `deploy/nginx/unigraph.conf.example`：传统部署
- `deploy/nginx/default.conf.template`：Docker 镜像

构建前端后，将 `frontend/dist` 同步到 `/var/www/unigraph`，修改示例中的域名，然后启用站点。配置已经包含：

- `/` 提供前端静态资源和 SPA 回退；
- `/knowg/` 反向代理到后端 `8000`；
- 问答流关闭代理缓冲，读写超时为 600 秒；
- 上传请求最大 50 MiB；
- 基础安全响应头。

启用 HTTPS 时建议使用 Certbot、云负载均衡或组织统一证书平台，并把 HTTP 重定向到 HTTPS。

### 3.7 Linux systemd 托管

仓库提供两个可修改的服务文件：

- `deploy/systemd/unigraph-backend.service`
- `deploy/systemd/unigraph-celery.service`

默认假设代码位于 `/opt/unigraph`、虚拟环境位于 `/opt/unigraph/.venv`、运行用户为 `unigraph`、环境文件位于 `/etc/unigraph/unigraph.env`。

```bash
sudo install -m 0644 deploy/systemd/unigraph-backend.service /etc/systemd/system/
sudo install -m 0644 deploy/systemd/unigraph-celery.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now unigraph-backend unigraph-celery
sudo systemctl status unigraph-backend unigraph-celery
```

环境文件权限应限制为运行用户和管理员可读：

```bash
sudo chown root:unigraph /etc/unigraph/unigraph.env
sudo chmod 0640 /etc/unigraph/unigraph.env
```

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
- `AUTH_AES_SECRET_KEY`
- `LLM_API_KEY_ENCRYPTION_KEY`
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

先把 `.env.docker` 中的 `ENVIRONMENT` 改为 `pro`、`COOKIE_SECURE` 改为 `true`，并将 `CORS_ALLOWED_ORIGINS` 设置为真实 HTTPS Origin。生产模式会拒绝占位密钥、短密钥、通配 CORS 和不安全 Cookie。

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
- 后端健康检查：`http://localhost:8000/knowg/v1/health`

后端与前端都配置了容器健康检查；前端会等待后端健康后再启动。后端镜像使用多阶段构建并以 UID/GID `10001` 的非 root 用户运行。Linux 主机首次启动前请确保绑定目录可写：

```bash
mkdir -p var backend/static
sudo chown -R 10001:10001 var backend/static
```

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

升级已有数据库时，请按文件名顺序执行 `backend/migrations/` 中尚未应用的 SQL。首次启动的新数据库无需重复执行这些迁移。

`20260730_multi_user_constraints.sql` 会把知识库和模型提供商名称约束调整为“用户内唯一”，并扩大模型密钥字段以保存密文。旧的明文模型密钥会在首次实际使用时自动改写为密文。

升级已有数据库前先备份，然后按文件名顺序只执行尚未应用的迁移：

```bash
mysqldump -uroot -p --single-transaction onlineunigraph > unigraph-backup.sql
mysql -uroot -p onlineunigraph < backend/migrations/20260724_chat_history.sql
mysql -uroot -p onlineunigraph < backend/migrations/20260728_chat_share.sql
mysql -uroot -p onlineunigraph < backend/migrations/20260730_multi_user_constraints.sql
```

新数据库由 `deploy/mysql/init/01-schema.sql` 创建最终结构，不要再重复执行上述迁移。

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
- `deploy/nginx/unigraph.conf.example`
- `deploy/nginx/40-runtime-config.sh`
- `deploy/systemd/unigraph-backend.service`
- `deploy/systemd/unigraph-celery.service`
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

## 8. 验收与排障

### 8.1 健康检查

```bash
curl --fail http://127.0.0.1:8000/knowg/v1/health
docker compose --env-file .env.docker ps
```

健康接口返回 `{"status":"ok"}`。如果后端容器不健康，先检查 MySQL、Redis 和环境变量：

```bash
docker compose --env-file .env.docker logs --tail=200 mysql redis backend
```

### 8.2 流式问答没有逐字显示

确认反向代理已设置 `proxy_buffering off`，没有在上层 CDN 再次缓冲 NDJSON 响应，并检查语言模型和嵌入模型是否分别通过个人中心连接测试。

### 8.3 构建索引失败

索引同时依赖语言模型与嵌入模型。社区报告使用语言模型，实体向量使用嵌入模型；任何嵌入失败都会使任务失败。修改配置后重新运行原任务即可，不会在任务中心创建重复记录。

### 8.4 API Key 显示为空

这是安全行为：后端不会把保存的明文密钥返回给浏览器。个人中心显示“已保存”即表示数据库中已有加密密钥；编辑时留空不会覆盖它。
