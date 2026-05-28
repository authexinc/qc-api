#!/bin/bash
set -e

echo "=== 1. Creating Database Tables ==="
/qc-api/venv/bin/python3 /qc-api/db/model.py
echo "Database tables checked/created."

echo "=== 2. Enabling and Starting systemd Service ==="
systemctl daemon-reload
systemctl enable qc-log-api.service
systemctl restart qc-log-api.service
echo "Systemd service qc-log-api started."

echo "=== 3. Enabling Nginx Configuration ==="
ln -sf /etc/nginx/sites-available/qc-log-api /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
echo "Nginx reloaded."

echo "=== 4. Opening Firewall Ports ==="
if command -v ufw >/dev/null 2>&1; then
    ufw allow 80/tcp
    echo "Firewall rules updated for port 80."
else
    echo "UFW not found, skipping firewall rule."
fi

echo "=== Deployment Completed Successfully! ==="
