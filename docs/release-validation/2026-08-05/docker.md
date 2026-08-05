# Docker 部署验证记录（2026-08-05）

## 结论

使用全新 Compose 项目名和全新 MySQL/Redis volume 实际启动成功。数据库初始化、Alembic 迁移、API、Nginx、四个独立 Celery worker、验证码代理、CORS 和缓存策略均已验证。

## 环境与隔离

- Docker Engine 27.5.1
- Docker Compose 2.32.4-desktop.1
- Compose project：`unigraph_validation`
- 端口：frontend `18080`、backend `18000`、MySQL `13306`、Redis `16379`
- 镜像：`unigraph-backend:local`、`unigraph-frontend:local`
- 数据卷：`unigraph_validation_mysql_data`、`unigraph_validation_redis_data`

## 已通过

- 开发与生产 Compose 配置均可解析。
- 后端和前端镜像从当前工作区成功构建。
- 全新 MySQL 初始化后，`migrate` 以退出码 0 完成，`alembic current` 为 `20260805_baseline (head)`。
- `backend`、`frontend`、`mysql`、`redis` 健康；四个 Celery worker 正常在线。
- worker 实际监听独立 direct exchange 与 routing key：`default`、`qa`、`indexing`、`migration`。
- `GET http://127.0.0.1:18000/knowg/v1/health` 返回 200。
- `GET http://127.0.0.1:18080/unigraph/login` 返回 200，Playwright 公共页面冒烟 2 项通过。
- 登录页实机截图保存在 `screenshots/docker-login.png`，验证码和页面样式均正常显示。
- `GET /knowg/v1/auth/captcha` 经前端 Nginx 代理返回 200、Base64 图片数据正常。
- 允许 Origin `http://127.0.0.1:18080` 的预检返回 200，并返回匹配的 `Access-Control-Allow-Origin`；未允许 Origin 返回 400。
- `/unigraph/config.js` 返回 `Cache-Control: no-store`。
- hashed asset 返回 `Cache-Control: public, max-age=31536000, immutable`，不存在重复缓存指令。
- 动态模块加载错误的一次性刷新恢复由 Vitest 覆盖，真实构建产物可通过 `/unigraph/assets/` 加载。

## 发现并修复

- `.env.docker.example` 原 `AUTH_AES_SECRET_KEY` 不是合法 Base64，导致首次后端启动失败。现已换成可启动但会被生产校验拒绝的 `changeme` 开发密钥，并同步修正传统部署模板。
- 初次队列声明虽然队列名不同，但 exchange/routing key 仍显示为 default。现已改为 `unigraph` direct exchange，并为四个队列设置同名 routing key；容器内 `inspect active_queues` 已确认。
- Nginx 同时使用 `expires` 和显式 `Cache-Control` 导致资源响应出现重复 max-age，现已改为单一明确的 immutable 响应头。
- 前端构建镜像和 CI 原使用 Node 20，但 `vue-i18n` 与测试运行时要求 Node 22。现已统一到 Node 22，并在 `package.json` 声明最低版本 `22.22.2`；最终镜像无引擎不兼容警告并构建成功。

## 环境限制与未执行项

- 未配置真实模型服务密钥，因此没有在该隔离栈执行付费模型调用及完整知识构建业务链路。
- 未模拟蓝绿双版本并存的旧标签页；一次性 chunk 恢复逻辑由单元测试覆盖，Nginx 404/缓存路径由实际容器验证。
- 未执行 Linux 主机重启、systemd 自启动或真实 HTTPS 域名证书验证。
