# Contributing to Theta-Prime

Thanks for your interest in contributing. This document covers the workflow for bug reports, features, and pull requests.

---

## Getting Started

1. Fork the repository and clone your fork
2. Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

3. Install frontend dependencies:

```bash
cd frontend && npm install
```

---

## Development Workflow

### Branch naming

| Type | Pattern |
|---|---|
| Bug fix | `fix/short-description` |
| Feature | `feat/short-description` |
| Documentation | `docs/short-description` |
| Refactor | `refactor/short-description` |

### Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) style:

```
feat: add watchlist batch-scan endpoint
fix: handle empty VIX DataFrame gracefully
docs: update API reference table in README
test: add Black-Scholes unit tests
```

---

## Backend (Python / FastAPI)

- Code lives in `backend/` and `scripts/`
- Run the dev server: `PYTHONPATH=. uvicorn backend.api.index:app --reload`
- Lint: `flake8 backend/ scripts/ --max-line-length 120`
- Tests: `pytest tests/ -v`

---

## Frontend (Next.js / TypeScript)

- Code lives in `frontend/`
- Run the dev server: `cd frontend && npm run dev`
- Type-check: `npx tsc --noEmit`
- Lint: `npx eslint . --ext .ts,.tsx`

---

## C++ Engine

The `fast_greeks` module is built with pybind11. To rebuild after changes:

```bash
pip install -e .
```

---

## Pull Request Checklist

- [ ] Tests pass locally (`pytest tests/ -v`)
- [ ] Frontend type-check passes (`npx tsc --noEmit`)
- [ ] No new flake8 errors at `--max-line-length 120`
- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] PR description explains what changed and why

---

## Reporting Bugs

Open a GitHub issue with:
- Steps to reproduce
- Expected vs actual behaviour
- Python version, OS, and relevant error output
