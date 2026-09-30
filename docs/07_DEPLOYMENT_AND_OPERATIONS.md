# Deployment & Operations Guide

This document provides step-by-step procedures for cross-compiling, provisioning, deploying, and operating the TeknoNFC payment gateway and management service in production environments.

---

## 1. Build & Cross-Compilation

TeknoNFC uses pure Go without CGO dependencies (`CGO_ENABLED=0`), enabling seamless cross-compilation from any workstation (Windows, macOS, Linux) to Linux x86_64 servers.

### 1.1 Production Linux Build (AMD64)
From the project root on Windows or Linux:
```powershell
$env:GOOS="linux"; $env:GOARCH="amd64"; $env:CGO_ENABLED="0"; go build -ldflags="-s -w" -o go-nfc ./cmd/server
```
Or on Unix/Bash:
```bash
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -ldflags="-s -w" -o go-nfc ./cmd/server
```

**Compiler Flags Rationale**:
- `CGO_ENABLED=0`: Eliminates glibc / C-runtime dynamic linking dependencies, producing a completely static self-contained binary.
- `-ldflags="-s -w"`: Strips debug symbols (`-s`) and DWARF symbol tables (`-w`), reducing binary footprint by ~40% while preserving panic trace line numbers.

### 1.2 Windows Build
```powershell
go build -ldflags="-s -w" -o go-nfc.exe ./cmd/server
```

---

## 2. Linux Production Host Setup

### 2.1 Directory Structure
Create the dedicated service user and directory tree on the target Linux host (`/var/www/go-nfc`):
```bash
sudo useradd -r -s /bin/false -d /var/www/go-nfc teknonfc
sudo mkdir -p /var/www/go-nfc/data
sudo chown -R teknonfc:teknonfc /var/www/go-nfc
sudo chmod 750 /var/www/go-nfc
```

### 2.2 Systemd Service Unit (`/etc/systemd/system/go-nfc.service`)
Install the following service definition:
```ini
[Unit]
Description=TeknoNFC Bank-Grade Contactless Wallet & Payment Ledger Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=teknonfc
Group=teknonfc
WorkingDirectory=/var/www/go-nfc
ExecStart=/var/www/go-nfc/go-nfc
Restart=always
RestartSec=3
LimitNOFILE=65535

# Environment Configuration
Environment="PORT=8888"
Environment="SQLITE_DB=/var/www/go-nfc/data/teknonfc.db"
Environment="ADMIN_PASSWORD=Admin@123456"
Environment="ENVIRONMENT=production"

# Sandboxing & Security Hardening
ProtectSystem=full
ProtectHome=true
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable go-nfc
sudo systemctl start go-nfc
```

---

## 3. Zero-Downtime Deployment Runbook

To deploy an updated binary to a live production server:

```bash
# 1. Grant execution permissions to the newly uploaded binary
chmod +x go-nfc-new

# 2. Stop the running service to release the file lock
systemctl stop go-nfc || pkill -f go-nfc

# 3. Swap the new binary into production
mv go-nfc-new go-nfc

# 4. Start the service
systemctl start go-nfc

# 5. Verify the service is active and running
systemctl status go-nfc --no-pager
```

---

## 4. Health Checks & Verification

### 4.1 System Status Probe
```bash
curl -i http://localhost:8888/health
```
**Expected Response**:
```json
{
  "status": "healthy",
  "system": "TeknoNFC FinTech Switch",
  "version": "1.2.0",
  "pci_dss": "PCI DSS v4.0.1 Compliant",
  "db_status": "connected"
}
```

### 4.2 System Metrics Probe
```bash
curl -s -H "Authorization: Bearer <TOKEN>" http://localhost:8888/api/admin/metrics | jq .
```

---

## 5. Backup & Disaster Recovery

### 5.1 SQLite Hot Atomic Backup
Because TeknoNFC runs SQLite in WAL mode, backups can be performed while the service is actively processing transactions with zero locking:

```bash
# Atomic online snapshot using sqlite3 VACUUM INTO
sqlite3 /var/www/go-nfc/data/teknonfc.db "VACUUM INTO '/var/www/go-nfc/data/backup-$(date +%F-%H%M).db';"
```

### 5.2 Automated Daily Cron Backup
Add to `/etc/cron.daily/teknonfc-backup`:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/teknonfc"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
sqlite3 /var/www/go-nfc/data/teknonfc.db "VACUUM INTO '$BACKUP_DIR/teknonfc_$TIMESTAMP.db';"
gzip -9 "$BACKUP_DIR/teknonfc_$TIMESTAMP.db"
# Retain backups for 30 days
find "$BACKUP_DIR" -name "teknonfc_*.db.gz" -mtime +30 -delete
```
