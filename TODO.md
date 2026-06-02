# Project Todo

## Code Quality

- [x] Replace `datetime.utcnow()` with timezone-aware UTC datetime usage.
- [x] Replace legacy `Query.get()` calls with `db.session.get(...)`.
- [x] Investigate and fix sqlite resource warnings in the test suite.
- [x] Review the shadowed legacy `app/auth.py` file and remove it if it is no longer needed.
- [x] Remove stale commented-out code from the application factory.
- [x] Replace broad route-level comments with clearer names or helper functions where possible.
- [x] Decide whether to keep both Ruff format and Black, or simplify to one formatter.
- [x] Move repeated test setup helpers into reusable fixtures.

## API Behavior

- [ ] Decide whether user CRUD endpoints should require JWT authentication.
- [ ] Add request validation for user payloads.
- [ ] Add a maximum allowed `limit` for paginated user listing.
- [ ] Return consistent JSON error responses for 400, 401, 404, and 500 cases.
- [ ] Add tests for malformed JSON request bodies.
- [ ] Add tests for pagination edge cases.
- [ ] Add tests for invalid sort and order query parameters.
- [ ] Consider adding admin/user role checks before modifying users.
- [ ] Require JWT authentication for file storage endpoints.
- [ ] Add semantic S3 sub-prefixes for file categories such as user profile images.

## Security And Config

- [x] Move hardcoded secrets and connection strings to environment variables.
- [x] Configure `SECRET_KEY`.
- [x] Configure `JWT_SECRET_KEY`.
- [x] Configure `SQLALCHEMY_DATABASE_URI`.
- [x] Configure `CACHE_REDIS_URL`.
- [x] Use a stronger JWT secret for local/dev/test settings.
- [x] Add `.env.example` with documented development defaults.
- [ ] Require real `SECRET_KEY` and `JWT_SECRET_KEY` in production.
- [x] Split configuration by environment: development, testing, production.
- [ ] Move MySQL passwords in `docker-compose.yaml` behind environment variables.
- [ ] Add password policy or stronger admin seed password handling.
- [ ] Add token expiration tests.
- [ ] Consider refresh tokens or token revocation if sessions need longer lifetimes.
- [ ] Create a least-privilege IAM identity for local S3 development instead of using the administrator profile.
- [ ] Create a least-privilege EC2 IAM role and instance profile for S3, Parameter Store, ECR, and Systems Manager access.

## Docker

- [x] Add a `.dockerignore` file.
- [x] Exclude `venv/`, `.git/`, `.cache/`, logs, pycache, coverage files, and local editor files from Docker build context.
- [x] Re-run `docker build .` and confirm the build context is smaller.
- [ ] Use a production WSGI server such as Gunicorn instead of `flask run` for non-development images.
- [ ] Add a non-root user to the Docker image.
- [ ] Optimize Docker layer caching by copying `requirements.txt` before the rest of the source.
- [x] Add a Docker healthcheck.
- [ ] Split production dependencies into `requirements.txt` and development/test tools into `requirements-dev.txt`.

## Database And Migrations

- [ ] Document how to run database migrations locally.
- [ ] Add a repeatable command for seeding the default admin user.
- [ ] Review migration workflow in Docker Compose.
- [ ] Add database indexes if user lookup grows beyond the demo dataset.
- [ ] Decide whether `Dummy` model is still needed.
- [ ] Create an AWS RDS MySQL instance for staging.
- [ ] Store the RDS database URL and password outside the repository.
- [ ] Run migrations against staging RDS during deployment.

## Integration Testing

- [ ] Keep the fast unit-test suite on in-memory SQLite.
- [ ] Adapt reusable database fixtures so integration tests can run against MySQL 8.
- [ ] Add a MySQL 8 service container to GitHub Actions for integration tests.
- [ ] Run database migrations against disposable MySQL before integration tests.
- [ ] Add Redis integration tests with a disposable Redis service container.
- [ ] Keep tests that require real AWS resources separate from the normal CI suite.

## GitHub

- [ ] Protect the `main` branch.
- [ ] Require CI checks before merging.
- [ ] Require CodeQL checks before merging.
- [ ] Require dependency audit checks before merging.
- [x] Add README badges for CI, CodeQL, dependency audit, and Docker build.
- [x] Add README quality checks documentation.
- [x] Add workflow comments describing current CI behavior.
- [ ] Decide whether to keep direct pushes to `main` or move to a pull-request workflow.
- [ ] If direct pushes stay, document that failed checks are reported after the push lands.
- [ ] If PRs are introduced, require CI, CodeQL, dependency audit, and Docker checks before merging.
- [ ] Consider enabling signed commits later if commit provenance becomes important.
- [ ] Add scheduled dependency audit runs in addition to push-based runs.
- [ ] Add automatic EC2 deployment with GitHub Actions OIDC, ECR images, and Systems Manager Run Command.

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
- [ ] Add curl examples for login, protected requests, and user CRUD.
- [x] Add environment variable documentation to the README.
- [ ] Add API error response examples to `docs/openapi.yaml`.

## Observability

- [ ] Make log level configurable by environment.
- [ ] Avoid global `logging.basicConfig` side effects at import time.
- [ ] Use structured or consistent request logging.
- [x] Add lightweight health and readiness endpoints.
- [ ] Decide where application logs should go in Docker and production.

## Deployment

- [ ] Choose a deployment target.
- [ ] Evaluate Render.
- [ ] Evaluate Railway.
- [ ] Evaluate Fly.io.
- [ ] Evaluate Docker-based VPS deployment.
- [ ] Define the staging environment after production-shaped AWS integration is stable.
- [ ] Configure managed Redis before RDS to validate the existing cache integration.
- [ ] Create an AWS ElastiCache Redis service for staging.
- [ ] Wire the app to the ElastiCache primary endpoint with `CACHE_REDIS_URL`.
- [ ] Create an application EC2 security group and allow Redis 6379 from that app security group.
- [ ] Run the ElastiCache smoke test from EC2 or SSM inside the VPC before enabling it as a required readiness check.
- [ ] Enable `READINESS_CHECK_CACHE=true` in staging after Redis is required.
- [ ] Choose a production database provider.
- [ ] Choose a production Redis provider or disable Redis cache if unnecessary.
- [ ] Document deployment environment variables.
- [ ] Add deployment smoke-test steps.
- [ ] Define an ephemeral AWS staging environment with Terraform.
- [ ] Add a manual GitHub Actions workflow to provision the ephemeral Terraform stack on demand.
- [ ] Deploy the application, run migrations, verify `/ready`, and run integration smoke tests against ephemeral staging.
- [ ] Destroy the ephemeral Terraform stack even when the validation workflow fails.
- [ ] Store Terraform state safely and document recovery steps for failed stack cleanup.
