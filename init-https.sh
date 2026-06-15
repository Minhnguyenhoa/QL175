#!/bin/sh
# One-shot: obtain a Let's Encrypt certificate for resalloc.site and switch nginx to HTTPS.
# PREREQUISITE: resalloc.site (and www) must already resolve to THIS server's public IP,
# and inbound ports 80 + 443 must be open. Run from the project root: sh init-https.sh
set -e

DOMAIN="resalloc.site"
WWW="www.resalloc.site"
EMAIL="khicongkhanh@gmail.com"
STAGING=""   # set to "--staging" to test without hitting rate limits

cd "$(dirname "$0")"
mkdir -p certbot/conf certbot/www

echo "==> Checking DNS for $DOMAIN ..."
if ! nslookup "$DOMAIN" 8.8.8.8 >/dev/null 2>&1; then
  echo "!! $DOMAIN does not resolve yet. Point an A record to this server first, then re-run."
  exit 1
fi

echo "==> Making sure the HTTP (port 80) site is up so the ACME challenge can be served ..."
docker compose up -d frontend backend

echo "==> Requesting certificate from Let's Encrypt ..."
docker compose run --rm --entrypoint certbot certbot certonly \
  --webroot -w /var/www/certbot \
  -d "$DOMAIN" -d "$WWW" \
  --email "$EMAIL" --agree-tos --no-eff-email $STAGING

echo "==> Certificate obtained. Switching nginx to the HTTPS config ..."
# The container reads frontend/nginx.conf via a bind-mount, so overwrite it on the host and reload.
cp frontend/nginx.conf frontend/nginx-http.conf.bak
cp frontend/nginx-https.conf frontend/nginx.conf
docker compose exec -T frontend nginx -t
docker compose exec -T frontend nginx -s reload

echo "==> Done. https://$DOMAIN should now work (HTTP auto-redirects to HTTPS)."
echo "    Renewals run automatically via the 'certbot' service; after a renewal run:"
echo "      docker compose exec frontend nginx -s reload"
