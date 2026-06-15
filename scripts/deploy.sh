#!/usr/bin/env bash
# ============================================================================
# VPS deploy script — pulls pre-built images from GHCR and restarts services.
# Invoked automatically by GitHub Actions over SSH, or run manually on the VPS.
#
#   GHCR_USER / GHCR_TOKEN  (optional) -> docker login to ghcr.io for private images
#
# It does NOT build anything and NEVER touches certbot/conf (live certs live there).
# ============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."
COMPOSE="docker compose -f docker-compose.prod.yml"

echo "==> [1/5] Sync deploy config from git (selective — certbot/conf is left untouched)"
git fetch origin main
# Only refresh the files the VPS actually needs. Never blanket-reset, so local
# certbot renewal state (certbot/conf/renewal/*.conf) is preserved.
git checkout origin/main -- \
  docker-compose.prod.yml \
  frontend/nginx.conf \
  database \
  scripts/deploy.sh

if [ -n "${GHCR_TOKEN:-}" ]; then
  echo "==> [2/5] Login to GHCR"
  echo "$GHCR_TOKEN" | docker login ghcr.io -u "${GHCR_USER:-x}" --password-stdin
else
  echo "==> [2/5] No GHCR_TOKEN provided — assuming public images, skipping login"
fi

echo "==> [3/5] Pull latest images"
$COMPOSE pull

echo "==> [4/5] Restart services (db-seed stays off — it is behind the 'seed' profile)"
$COMPOSE up -d

echo "==> [5/5] Clean up dangling images"
docker image prune -f >/dev/null 2>&1 || true

echo "==> Done. Current status:"
$COMPOSE ps
