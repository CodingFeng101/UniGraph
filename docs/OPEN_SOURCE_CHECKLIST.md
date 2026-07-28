# 公开发布前清单

当前工作树已经移除环境文件、私钥、证书密码、运行日志、本地数据库、Python 缓存和未使用的第三方源码副本，并补齐了自动化安全检查。

## 已完成

- [x] 删除当前版本中的 `.env`、PFX、私钥、密码文件、日志、SQLite/Chroma 数据和缓存。
- [x] 收紧上传、模型密钥测试、生产 OpenAPI、CORS、服务端口和日志脱敏策略。
- [x] 从实际源码依赖重建 `backend/requirements.txt`，并通过 `pip-audit` 零已知漏洞检查。
- [x] 通过后端 Ruff、6 项安全回归测试和全新 Python 环境应用导入测试。
- [x] 通过前端 ESLint、TypeScript、生产构建和 npm 高危漏洞检查。
- [x] 通过开发与生产 Compose 配置解析。
- [x] 补齐 README、MIT License、第三方声明、安全政策、贡献指南、CI 和 Dependabot。
- [x] 生成不包含旧 Git 历史的干净发布仓库 `.codex-release-git`。

## 发布者仍需完成

- [ ] 在各服务控制台轮换所有曾提交过的数据库密码、JWT 密钥、OAuth 密钥、LLM API Key、证书和 PFX 密码。删除文件不能撤销已经泄露的凭据。
- [ ] 使用全新凭据从 `.codex-release-git` 创建新的公开仓库；不要直接公开当前仓库的旧历史。
- [ ] 使用全新 `.env.docker` 从零启动 Compose，人工验证注册、登录、文件上传、图谱构建和问答主流程。
- [ ] 在 GitHub 启用 Secret Scanning、Dependabot alerts、分支保护和必需 CI 检查。

## 如果必须保留旧提交历史

先做镜像备份并通知所有协作者，再在仓库副本中使用 `git-filter-repo` 删除以下路径及源码中出现过的真实密钥：

```bash
git filter-repo --sensitive-data-removal --invert-paths \
  --path backend/.env \
  --path backend/.env.dev \
  --path backend/.env.prod \
  --path frontend/.env.development \
  --path frontend/.env.production \
  --path frontend/Apache \
  --path frontend/IIS \
  --path backend/log \
  --path celery.log \
  --path backend/embedding/web_data_embeddings/chroma.sqlite3 \
  --path backend/common/core_layer/unigraph/web_search/web_data_embeddings/chroma.sqlite3 \
  --path-glob '*/__pycache__/*' \
  --path-glob '*.pyc'
```

历史改写后必须重新扫描全部分支与标签，并协调强制推送和协作者重新克隆。对首次公开发布而言，使用已生成的单提交干净仓库更简单、安全。
