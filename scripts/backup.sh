#!/usr/bin/env bash
set -euo pipefail
export PATH=/usr/local/bin:/usr/bin:/bin

cd "$(dirname "$0")/.."
umask 077
stamp=$(date +%Y%m%d_%H%M%S)
tmp="backups/.partial_${stamp}.dump"
final="backups/assetsys_${stamp}.dump"

trap 'rm -f "$tmp"' EXIT
trap 'echo "$(date -Is) FAILED" >&2' ERR

docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$tmp"
docker compose exec -T db pg_restore --list < "$tmp" > /dev/null
mv "$tmp" "$final"
find backups -name 'assetsys_*.dump' -mtime +14 -delete
echo "$(date -Is) OK $final $(stat -c %s "$final") bytes"
