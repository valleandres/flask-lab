# flask-lab

[![CI](https://github.com/valleandres/flask-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/valleandres/flask-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/valleandres/flask-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/valleandres/flask-lab/actions/workflows/codeql.yml)
[![Dependencies](https://github.com/valleandres/flask-lab/actions/workflows/dependencies.yml/badge.svg)](https://github.com/valleandres/flask-lab/actions/workflows/dependencies.yml)
[![Docker](https://github.com/valleandres/flask-lab/actions/workflows/docker.yml/badge.svg)](https://github.com/valleandres/flask-lab/actions/workflows/docker.yml)

`flask-lab` is a Flask application for practicing production-style Python web
development. It includes REST endpoints, SQLAlchemy models, JWT authentication,
unit tests, local quality checks, Docker support, and GitHub Actions workflows
for CI, dependency auditing, CodeQL, and Docker image validation.

## development setup

Add the local development hostname:

```bash
echo "127.0.0.1 flask.local" | sudo tee -a /etc/hosts
```

Install `uv`:

```bash
python3 -m pip install uv
```

Create the existing `venv/` virtual environment and install dependencies with
`uv`:

```bash
uv venv venv
source venv/bin/activate
uv pip install -r requirements.txt
```

`requirements.txt` is still the dependency source for this project. `uv` is
used here as a faster environment and package installer.

The existing `venv/` directory can be managed by either `uv` or standard
`venv`/`pip` commands. Prefer one workflow per setup session to avoid confusing
your local environment.

Create the local development environment file and run the app with Docker
Compose:

```bash
cp .env.development.example .env.development
ENV_FILE=.env.development docker compose up -d
```

Open:

```text
http://flask.local/
```

## tests

Run the unit tests in Docker:

```bash
docker compose run --rm test
```

Run the unit tests locally:

```bash
pytest
```

Run the Postman collection with Newman:

```bash
npm install -g newman
newman run postman/flask-lab.postman_collection.json
```

## quality checks

GitHub Actions runs the project checks on every push to `main`.

- CI verifies Python syntax, tests with 100% coverage, Ruff, Pylint, Black, isort, Bandit, pre-commit hooks, and Docker image builds.
- CodeQL scans the Python code for security issues and publishes code scanning results.
- Dependency audit checks installed Python packages with `pip-audit`.
- Docker validates that the application image can be built from the current source.

Useful local commands:

```bash
uv pip install black isort bandit pylint ruff pytest-cov pre-commit
pytest --cov=app --cov-report=term-missing --cov-fail-under=100
ruff check app test migrations
ruff format --check app test migrations
pylint --rcfile=.pylintrc app test
black --check app test migrations
isort --check-only app test migrations
bandit -r app --skip B106
pre-commit run --all-files
docker build .
```

## API

The API is documented with OpenAPI in
[docs/openapi.yaml](docs/openapi.yaml).

### environment files

Only safe environment templates are versioned. Real environment files are
ignored by Git:

- `.env.development` for local development and Docker Compose.
- `.env.production` for AWS/production-shaped runs.

Create them from the templates:

```bash
cp .env.development.example .env.development
cp .env.production.example .env.production
```

Docker Compose loads the file selected by `ENV_FILE`:

```bash
ENV_FILE=.env.development docker compose up -d
ENV_FILE=.env.production docker compose up -d web
```

Use the `web` service when running with `.env.production` so the app uses AWS
RDS, ElastiCache, and S3 instead of relying on the local support containers.
The local `db` and `redis` services remain available for development.

When running Flask directly from the host, pass the same selector:

```bash
ENV_FILE=.env.development flask --app app:create_app run --port 5000
ENV_FILE=.env.production flask --app app:create_app run --port 5000
```

Environment variables already exported in the shell take precedence over values
loaded from the selected file.

`APP_ENV` selects one of the application configurations:

```dotenv
APP_ENV=development
```

- `development` enables debug mode and local development defaults.
- `testing` uses SQLite, simple in-process cache, and local file storage.
- `staging` is intentionally pending until the intermediate AWS environment is
  created.
- `production` uses AWS S3 for private file storage and AWS ElastiCache Redis
  for cache. It requires `SECRET_KEY`, `JWT_SECRET_KEY`,
  `SQLALCHEMY_DATABASE_URI`, `CACHE_REDIS_URL`, and `S3_BUCKET_NAME` to be set
  explicitly.

The intended environment split is:

- Development: local Docker Compose services only, no AWS dependency.
- Staging: pending future intermediate AWS environment.
- Production: AWS S3 and AWS ElastiCache, with database configuration supplied
  by the deployment environment.

### database and cache

Docker Compose provides local MySQL and Redis services for development. This is
the default local setup and does not require AWS:

```dotenv
SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:password@db:3306/mydatabase
CACHE_TYPE=RedisCache
CACHE_REDIS_URL=redis://redis:6379/0
CACHE_DEFAULT_TIMEOUT=60
CACHE_KEY_PREFIX=flask-lab:
READINESS_CHECK_CACHE=false
```

RDS is the managed MySQL database, not the cache. When using AWS RDS, point the
database URL at the RDS endpoint:

```dotenv
SQLALCHEMY_DATABASE_URI=mysql+pymysql://<user>:<password>@<rds-endpoint>:3306/<database>
```

For AWS-managed cache, use ElastiCache for Redis and point the cache URL at the
Redis primary endpoint:

```dotenv
CACHE_TYPE=RedisCache
CACHE_REDIS_URL=rediss://:<auth-token>@<elasticache-primary-endpoint>:6379/0
READINESS_CHECK_CACHE=true
```

The `:` before `<auth-token>` is required when Redis uses a password without a
username. Use `redis://...` only when the Redis service does not use in-transit
encryption. Keep database passwords and cache credentials in the deployment
secret manager, not in this repository. If Redis is not available for a local
run outside Docker Compose, set `CACHE_TYPE=SimpleCache`.

Use [.env.production.example](.env.production.example) as the production-shaped
template. Keep real values in `.env.production` for manual testing, or in a
deployment secret store for deployed environments.

For local file storage, keep:

```dotenv
STORAGE_BACKEND=local
LOCAL_UPLOAD_FOLDER=uploads
```

Uploaded files are written below `uploads/`, which is also ignored by Git.

For private S3 storage, configure:

```dotenv
STORAGE_BACKEND=s3
AWS_REGION=us-east-2
S3_BUCKET_NAME=flask-lab-andres-dev
S3_UPLOAD_PREFIX=files
S3_PRESIGNED_URL_EXPIRATION=3600
```

The application uses the standard boto3 credential chain. In production on EC2,
prefer an instance profile/IAM role instead of `AWS_PROFILE`. Do not add AWS
credentials to `.env`. S3 uploads do not set public ACLs, and file access uses
expiring presigned URLs.

If you set `AWS_PROFILE` for manual local AWS testing, it is the AWS profile
name, not an access key. Credentials remain in the local AWS configuration
outside this repository. Each uploaded object gets a generated key such as
`files/<uuid>_report.pdf`, returned by `POST /files`.

Docker Compose mounts the local `~/.aws` directory read-only so manual local AWS
testing can use `AWS_PROFILE`. On EC2, prefer the instance profile/IAM role and
leave `AWS_PROFILE` unset.

Upload a file, request an access URL, and delete the file:

```bash
BASE_URL=http://flask.local
curl -F "file=@README.md" "$BASE_URL/files"
curl "$BASE_URL/files/url?key=<key>"
curl -X DELETE "$BASE_URL/files?key=<key>"
```

### operational checks

The app exposes two unauthenticated endpoints for container and infrastructure
monitoring:

```bash
BASE_URL=http://flask.local
curl "$BASE_URL/health"
curl "$BASE_URL/ready"
```

`GET /health` reports that the Flask process is running. `GET /ready` also
executes a lightweight database query and returns `503` when the app should not
receive traffic. Docker Compose uses `/health` for its container healthcheck.

## configuration

Development defaults live in [.env.development.example](.env.development.example).
Production-shaped defaults live in
[.env.production.example](.env.production.example). Keep secrets in ignored
local env files or in the secret manager used by the deployment environment.

## deployment

TODO: document the deployment target and release process.
