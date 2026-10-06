#!/bin/bash
# ==============================================================================
# DoseMitra AI (डोज़मित्र) - Production Platform Launcher
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "===================================================================="
echo " 🩺 Starting DoseMitra AI Full-Stack Platform"
echo " Project Directory: $PROJECT_DIR"
echo " Initializing CDSCO & PMBJP Jan Aushadhi Catalog..."
python3 -c "import database; database.init_db()"
echo " Database verified!"
echo "===================================================================="

# Start server
exec python3 main.py
