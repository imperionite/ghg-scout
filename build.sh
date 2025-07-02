#!/usr/bin/env bash
set -o errexit

echo "🚀 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🌱 Running initial database seed..."
python scripts/seed.py || echo "⚠️ Seed script failed or already seeded. Continuing build."

echo "✅ Build complete."
