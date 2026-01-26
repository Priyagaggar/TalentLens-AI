#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies (if not using Docker or pre-built env)
# pip install -r requirements.txt

# Download SpaCy model
echo "Downloading SpaCy model..."
python -m spacy download en_core_web_sm

# Initialize Database
echo "Running database migrations..."
python scripts/init_db.py

# Start Uvicorn
echo "Starting Application..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT
