# 传统部署验证记录（2026-08-05）

## 结论

传统部署的依赖安装、数据库版本检查、后端启动、前端构建和浏览器冒烟均通过。验证在独立目录 `D:\UniGraph-validation-traditional-2` 中进行，未复用项目原有虚拟环境和 `node_modules`。

## 环境

- Windows 11 10.0.26200
- Python 3.12.4
- Node.js 22.22.2 / npm 10.8.2
- MySQL 8.x 与 Redis 7.x 使用本机已有服务
- 基线提交：`47cd790`，另包含本次尚未提交的工作区修改

## 已通过

- 新建 Python 虚拟环境并按 `backend/requirements-dev.txt` 安装锁定依赖。
- 从空 `node_modules` 执行 `npm ci`。
- 后端测试：73 passed，1 skipped。跳过项仅为复制目录不包含 `.git` 元数据时无法执行 `git ls-files`；主工作区会执行该项。
- 后端运行时导入冒烟通过。
- Alembic migration head 为 `20260805_baseline`。
- 独立端口 `18001` 启动后端，`GET /knowg/v1/health` 返回 200 与 `{"status":"ok"}`，验证后已停止该进程。
- 前端 ESLint、TypeScript 检查、8 个 Vitest 测试和生产构建通过。
- Playwright 公共页面冒烟 2 项通过：登录页应用壳无运行时异常，运行时配置可加载。

## 环境限制与未执行项

- 本次使用独立复制目录模拟干净检出，不是另一台物理机，也未验证 Linux systemd 和整机重启。
- 为避免消费本机已有队列，未在传统部署副本中再次启动四个 Celery worker；队列启动与隔离已在独立 Docker 环境实际验证。
- 未在无真实模型测试密钥的环境中执行知识架构生成、图谱抽取、索引、知识迁移和问答的完整付费模型链路。
