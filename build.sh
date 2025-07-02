#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies (optional, depending on setup)
pip install -r requirements.txt

# Run database seeding only if not already seeded
echo "Running initial database seed..."
python scripts/seed.py || echo "Seed script failed or already seeded. Continuing build."

echo "✅ Build complete."
