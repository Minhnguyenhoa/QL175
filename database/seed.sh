#!/bin/sh
# One-shot data seeder.
# Schema is created by Hibernate (backend, ddl-auto=update). This script waits
# for the `customers` table to appear, then loads full_data.sql ONLY if the
# table is still empty -> safe to re-run, never overwrites live data.
set -e

HOST="${DB_HOST:-mysql}"
USER="${DB_USER:-root}"
PASS="${DB_PASSWORD:-123456}"
DB="${DB_NAME:-project_mgmt}"
SQL_FILE="/seed/full_data.sql"

run() { mysql -h "$HOST" -u "$USER" -p"$PASS" -N -B "$DB" -e "$1" 2>/dev/null; }

echo "[seed] waiting for schema (table 'customers') to be created by backend..."
i=0
until [ "$(run "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$DB' AND table_name='customers';")" = "1" ]; do
  i=$((i+1))
  if [ "$i" -gt 120 ]; then
    echo "[seed] timed out waiting for schema. Exiting."
    exit 0
  fi
  sleep 5
done

COUNT="$(run "SELECT COUNT(*) FROM customers;")"
if [ "$COUNT" -gt 0 ] 2>/dev/null; then
  echo "[seed] customers already has $COUNT rows -> skipping seed."
  exit 0
fi

echo "[seed] loading full_data.sql ..."
mysql -h "$HOST" -u "$USER" -p"$PASS" "$DB" < "$SQL_FILE"
echo "[seed] done. customers now has $(run "SELECT COUNT(*) FROM customers;") rows."
