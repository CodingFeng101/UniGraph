# Contributing

Thanks for improving UniGraph.

## Development workflow

1. Fork the repository and create a focused branch.
2. Keep changes small and explain the problem they solve.
3. Never commit `.env` files, credentials, logs, database files, generated
   assets, or user data.
4. Run the checks below before opening a pull request.

```bash
ruff format --check backend
ruff check backend
python -m unittest discover -s backend/tests -v
python backend/tests/smoke_import.py
pip-audit --requirement backend/requirements.txt --no-deps --disable-pip
cd frontend
npm ci
npm run lint
npm run typecheck
npm run build
npm audit --audit-level=high
```

For backend changes, add focused tests when a test seam exists. Avoid broad
format-only changes in the same pull request as functional work.

## Pull requests

Describe the behavior before and after the change, how it was verified, and
any migration or configuration impact. Link the relevant issue when one
exists.
