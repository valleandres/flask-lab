#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/flask-lab}"
IMAGE_URI="${IMAGE_URI:?IMAGE_URI is required}"
ENV_PARAMETER_NAME="${ENV_PARAMETER_NAME:-/flask-lab/dev/env-production}"
AWS_REGION="${AWS_REGION:-us-east-2}"
CONTAINER_NAME="${CONTAINER_NAME:-flask-lab-web}"

if ! command -v docker >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq ca-certificates curl docker.io
  sudo systemctl enable --now docker
fi

if ! command -v aws >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq awscli
fi

sudo mkdir -p "$APP_DIR"
sudo chown "$USER":"$USER" "$APP_DIR"

aws ssm get-parameter \
  --name "$ENV_PARAMETER_NAME" \
  --with-decryption \
  --region "$AWS_REGION" \
  --query 'Parameter.Value' \
  --output text > "$APP_DIR/.env.production"
chmod 600 "$APP_DIR/.env.production"

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "${IMAGE_URI%%/*}"

docker pull "$IMAGE_URI"
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --env-file "$APP_DIR/.env.production" \
  -p 80:5000 \
  "$IMAGE_URI"

for attempt in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:5000/ready >/dev/null; then
    echo "Deployment ready"
    exit 0
  fi
  sleep 2
done

docker logs "$CONTAINER_NAME" --tail 80 || true
echo "Deployment failed readiness check" >&2
exit 1
