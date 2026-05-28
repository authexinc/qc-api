#!/bin/bash
set -e

VERSION="0.0.59"
ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
    BINARY_ARCH="x86_64"
elif [ "$ARCH" = "aarch64" ]; then
    BINARY_ARCH="arm64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

PDC_TOKEN="$1"
PDC_CLUSTER="${2:-prod-us-east-0}"
PDC_GRAFANA_ID="${3:-1667369}"

if [ -z "$PDC_TOKEN" ]; then
    echo "Error: PDC Token is required."
    echo "Usage: $0 <PDC_TOKEN> [CLUSTER] [GRAFANA_ID]"
    exit 1
fi

URL="https://github.com/grafana/pdc-agent/releases/download/v${VERSION}/pdc-agent_Linux_${BINARY_ARCH}.tar.gz"

echo "=== 1. Downloading PDC Agent v${VERSION} (${BINARY_ARCH}) ==="
curl -L -o /tmp/pdc-agent.tar.gz "$URL"

echo "=== 2. Extracting Binary to /usr/local/bin ==="
tar -xzf /tmp/pdc-agent.tar.gz -C /tmp
mv /tmp/pdc-agent /usr/local/bin/pdc
chmod +x /usr/local/bin/pdc
rm -f /tmp/pdc-agent.tar.gz

echo "=== 3. Creating systemd Service for PDC Agent ==="
cat << EOF > /etc/systemd/system/pdc-agent.service
[Unit]
Description=Grafana Private Data Source Connect (PDC) Agent
After=network.target

[Service]
User=root
ExecStart=/usr/local/bin/pdc -token $PDC_TOKEN -cluster $PDC_CLUSTER -gcloud-hosted-grafana-id $PDC_GRAFANA_ID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "=== 4. Enabling and Starting pdc-agent Service ==="
systemctl daemon-reload
systemctl enable pdc-agent.service
systemctl restart pdc-agent.service

echo "=== PDC Agent Deployed & Started Successfully! ==="
systemctl status pdc-agent.service --no-pager

