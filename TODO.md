# Project Todo

## Code Quality

- [x] Replace `datetime.utcnow()` with timezone-aware UTC datetime usage.
- [x] Replace legacy `Query.get()` calls with `db.session.get(...)`.
- [x] Investigate and fix sqlite resource warnings in the test suite.
- [x] Review the shadowed legacy `app/auth.py` file and remove it if it is no longer needed.

## Security And Config

- [x] Move hardcoded secrets and connection strings to environment variables.
- [x] Configure `SECRET_KEY`.
- [x] Configure `JWT_SECRET_KEY`.
- [x] Configure `SQLALCHEMY_DATABASE_URI`.
- [x] Configure `CACHE_REDIS_URL`.
- [x] Use a stronger JWT secret for local/dev/test settings.

## Docker

- [x] Add a `.dockerignore` file.
- [x] Exclude `venv/`, `.git/`, `.cache/`, logs, pycache, coverage files, and local editor files from Docker build context.
- [x] Re-run `docker build .` and confirm the build context is smaller.

## GitHub

- [ ] Protect the `main` branch.
- [ ] Require CI checks before merging.
- [ ] Require CodeQL checks before merging.
- [ ] Require dependency audit checks before merging.
- [x] Add README badges for CI, CodeQL, dependency audit, and Docker build.
- [x] Add README quality checks documentation.
- [x] Add workflow comments describing current CI behavior.

## API Documentation

- [x] Document auth login endpoint.
- [x] Document protected endpoint usage.
- [x] Document create user endpoint.
- [x] Document list users endpoint.
- [x] Document update user endpoint.
- [x] Document delete user endpoint.
- [x] Consider adding an OpenAPI spec.
- [ ] Add OpenAPI spec validation to CI.
- [ ] Add response validation against the OpenAPI schema.
- [ ] Evaluate Schemathesis for generated API contract tests.
- [ ] Evaluate client generation from `docs/openapi.yaml`.

## Deployment

- [ ] Choose a deployment target.
- [ ] Evaluate Render.
- [ ] Evaluate Railway.
- [ ] Evaluate Fly.io.
- [ ] Evaluate Docker-based VPS deployment.
