#!/usr/bin/env bash
# Dumps the readings database and uploads it to the backups bucket.
set -euo pipefail

: "${WXDATA_DATABASE_URL:?set WXDATA_DATABASE_URL}"
: "${BACKUP_BUCKET:?set BACKUP_BUCKET}"

PG_DUMP_FLAGS=${PG_DUMP_FLAGS:-"--format=custom --no-owner --no-privileges"}
stamp=$(date -u +%Y%m%dT%H%M%SZ)
out="/tmp/wxdata-${stamp}.dump"

# PG_DUMP_FLAGS holds several flags, so it must word-split.
# shellcheck disable=SC2086
pg_dump $PG_DUMP_FLAGS --file="$out" "$WXDATA_DATABASE_URL"

# Upload to S3
aws s3 cp "$out" "s3://${BACKUP_BUCKET}/wxdata/${stamp}.dump" --only-show-errors
rm -f "$out"

keep_days=${KEEP_DAYS:-30}
cutoff=$(date -u -d "-${keep_days} days" +%Y%m%d 2>/dev/null || date -u -v-"${keep_days}"d +%Y%m%d)
aws s3 ls "s3://${BACKUP_BUCKET}/wxdata/" | awk '{print $4}' | while read -r name; do
  day=${name:0:8}
  if [[ "$day" < "$cutoff" ]]; then
    aws s3 rm "s3://${BACKUP_BUCKET}/wxdata/${name}" --only-show-errors
  fi
done
echo "Backed up to s3://${BACKUP_BUCKET}/wxdata/${stamp}.dump"
