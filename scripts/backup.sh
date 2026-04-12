#!/bin/sh
# Automated Database Backup Script
# Runs daily via cron or Docker container

set -e

POSTGRES_DB="${POSTGRES_DB:-cafe_db}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_HOST="${POSTGRES_HOST:-db}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"

# Create backup filename with timestamp
BACKUP_FILE="cafe_db_$(date +%Y%m%d_%H%M%S).sql.gz"

echo "Starting backup: ${BACKUP_FILE}"

# Perform backup
pg_dump -h "$POSTGRES_HOST" -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Verify backup
if [ -s "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
    echo "Backup completed: ${BACKUP_FILE}"
    ls -lh "${BACKUP_DIR}/${BACKUP_FILE}"
else
    echo "ERROR: Backup file is empty!"
    exit 1
fi

# Keep only last 7 backups (configurable)
cd "$BACKUP_DIR"
ls -t cafe_db_*.sql.gz | tail -n +8 | xargs -r rm

echo "Backup process complete"