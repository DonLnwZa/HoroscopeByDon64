# 📌 Rules: Cloud Deployment & Render Best Practices

## 1. Python Versioning
- Always explicitly set `PYTHON_VERSION=3.11.9` (or `3.11.x` / `3.12.x`) in `render.yaml` or cloud environment variables.
- Never rely on unpinned / latest preview Python runtimes (e.g. Python 3.14) that lack pre-compiled wheel binaries for C/Rust dependencies (`pydantic-core`, `ephem`, etc.).

## 2. Preventing Module Naming Collisions
- If a package directory named `app/` exists inside `backend/`, **never** name the main server entry script `app.py`. Name it `main.py` or `run.py`.
- Having both `backend/app/` and `backend/app.py` causes Python namespace import collision (`ModuleNotFoundError: No module named 'app'`).

## 3. Subdirectory Execution & Gunicorn Flags
- When backend entry point is nested inside subdirectories (e.g., `omni_oracle_app/backend`), always pass `--chdir` to Gunicorn:
  `gunicorn --chdir omni_oracle_app/backend main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

## 4. Frontend Relative API Endpoints
- In frontend code, never hardcode `http://localhost:5000` for API fetch calls.
- Always use relative paths like `/api/divine` or dynamic origins (`window.location.origin`) so that the application seamlessly works both locally and when deployed to production clouds.
