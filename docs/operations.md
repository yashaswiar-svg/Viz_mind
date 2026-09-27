# VizMind Operations & Maintenance Manual

This document details day-to-day operations, database migrations, backup procedures, and troubleshooting for VizMind.

---

## 🛠️ Database Migrations & Schema Updates

Migrations are powered by Alembic:
```bash
# Execute latest database migrations
docker compose exec backend alembic upgrade head

# Rollback one migration step
docker compose exec backend alembic downgrade -1

# Inspect current migration version
docker compose exec backend alembic current
```

---

## 💾 Backup & Restore Procedures

### Database Backup
```bash
docker compose exec db pg_dump -U vizmind -d vizmind > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Storage Backup
```bash
tar -cvzf storage_backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/storage/
```

---

## 🧹 Housekeeping & Cleanup

### Account Deletion Cleanup
User account deletion (`DELETE /api/v1/auth/me`) automatically:
1. Cascades database deletion for all dataset profiles, preprocessing runs, pattern results, anomaly records, prediction outputs, insights, and analyst conversations.
2. Deletes physical raw CSVs and preprocessed dataset files from `/app/storage`.

---

## 🔍 Monitoring & Incident Response

- Monitor endpoint responses and request execution rates via Uvicorn logs.
- Check database connection pool status on `/api/v1/health/ready`.
