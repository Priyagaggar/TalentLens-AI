#!/usr/bin/env bash
# Exit on error
set -o errexit

# Initialize Database
echo "Running database migrations..."
python scripts/init_db.py

# Start Uvicorn
echo "Starting Application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
