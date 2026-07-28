# UniGraph Backend

FastAPI API、Celery 任务和知识图谱业务代码位于此目录。所有命令默认从仓库根目录执行。

## 本地运行

```bash
cp backend/.env.template backend/.env
python -m venv .venv
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

`pyproject.toml` 是依赖声明源，`requirements.txt` 是部署使用的锁定文件。更新依赖后重新生成：

```bash
uv pip compile backend/pyproject.toml --output-file backend/requirements.txt --python-version 3.12 --cache-dir .cache/uv --no-emit-index-url
```

## 目录说明

- `app/`：API 路由、业务服务、数据模型与 Celery 任务。
- `common/`：公共组件和知识图谱核心能力。
- `core/`：应用配置、路径和注册逻辑。
- `database/`：MySQL、Redis 与会话管理。
- `migrations/`：增量 SQL 迁移。
- `tests/`：单元测试、安全回归和导入烟雾测试。

日志、上传文件和临时文件写入仓库根目录的 `var/`，不会混入源码目录。

## 检查

```bash
ruff format --check backend
ruff check backend
python -m unittest discover -s backend/tests -v
python backend/tests/smoke_import.py
```
