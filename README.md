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

Run the app with Docker Compose:

```bash
docker compose up web
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

## configuration

TODO: document environment variables for Flask, JWT, database, and Redis.

## deployment

TODO: document the deployment target and release process.
