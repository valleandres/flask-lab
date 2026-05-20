# Project Todo

## Code Quality

- [ ] Replace `datetime.utcnow()` with timezone-aware UTC datetime usage.
- [ ] Replace legacy `Query.get()` calls with `db.session.get(...)`.
- [ ] Investigate and fix sqlite resource warnings in the test suite.
- [x] Review the shadowed legacy `app/auth.py` file and remove it if it is no longer needed.

## Security And Config

- [ ] Move hardcoded secrets and connection strings to environment variables.
- [ ] Configure `SECRET_KEY`.
- [ ] Configure `JWT_SECRET_KEY`.
- [ ] Configure `SQLALCHEMY_DATABASE_URI`.
- [ ] Configure `CACHE_REDIS_URL`.
- [ ] Use a stronger JWT secret for local/dev/test settings.

## Docker

- [ ] Add a `.dockerignore` file.
- [ ] Exclude `venv/`, `.git/`, `.cache/`, logs, pycache, coverage files, and local editor files from Docker build context.
- [ ] Re-run `docker build .` and confirm the build context is smaller.

## GitHub

- [ ] Protect the `main` branch.
- [ ] Require CI checks before merging.
- [ ] Require CodeQL checks before merging.
- [ ] Require dependency audit checks before merging.
- [ ] Add README badges for CI, CodeQL, dependency audit, and Docker build.

## API Documentation

- [ ] Document auth login endpoint.
- [ ] Document protected endpoint usage.
- [ ] Document create user endpoint.
- [ ] Document list users endpoint.
- [ ] Document update user endpoint.
- [ ] Document delete user endpoint.
- [ ] Consider adding an OpenAPI spec.

## Deployment

- [ ] Choose a deployment target.
- [ ] Evaluate Render.
- [ ] Evaluate Railway.
- [ ] Evaluate Fly.io.
- [ ] Evaluate Docker-based VPS deployment.
