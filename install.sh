#!/bin/bash

# AbuseIPDB Nginx Blocker - Hypernode Installation Script
# Downloads and sets up the nginx blocker with cron automation for Hypernode servers

set -e

echo "=== AbuseIPDB Nginx Blocker - Hypernode Setup ==="

# Get current directory for installation
INSTALL_DIR="$(pwd)/AbuseIPDB-nginx-blocker"

# Download the main script if it doesn't exist
if [ ! -f "blocklist_updater.py" ]; then
    echo "Downloading blocklist_updater.py..."
    curl -s -o blocklist_updater.py https://raw.githubusercontent.com/hpowernl/AbuseIPDB-nginx-blocker/main/blocklist_updater.py
fi

# Make script executable
chmod +x blocklist_updater.py

echo "✓ Script downloaded and ready"

echo "✓ Setup ready"

# Script ready for use
echo "✓ Script ready for Hypernode server"

# Download and apply blocklist automatically
echo "Updating blocklist..."
python3 blocklist_updater.py
echo "✓ Blocklist updated successfully"

# Setup cron job for automatic updates every 4 hours
echo "Setting up automatic updates every 4 hours..."
CRON_JOB="0 */4 * * * cd $(pwd) && python3 blocklist_updater.py >/dev/null 2>&1"

# Check if cron job already exists
if ! crontab -l 2>/dev/null | grep -q "blocklist_updater.py"; then
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✓ Cron job added for automatic updates every 4 hours"
else
    echo "✓ Cron job already exists"
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "✓ AbuseIPDB nginx blocker ready!"
echo "✓ Automatic updates configured every 4 hours"
echo ""
