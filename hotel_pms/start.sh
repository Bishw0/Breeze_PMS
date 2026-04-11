#!/bin/bash
# Hotel PMS - Setup and Run Script
# Run this script to install dependencies, migrate, seed data, and start the server

set -e

echo "============================================"
echo "  Hotel Property Management System Setup"
echo "============================================"
echo ""

# Install dependencies
echo "[1/4] Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "[2/4] Running database migrations..."
python manage.py makemigrations rooms guests reservations billing staff
python manage.py migrate

echo ""
echo "[3/4] Seeding sample data..."
python manage.py seed_data

echo ""
echo "[4/4] Starting development server..."
echo ""
echo "============================================"
echo "  Hotel PMS is running!"
echo "  Open: http://127.0.0.1:8000"
echo "  Admin: http://127.0.0.1:8000/admin"
echo ""
echo "  Login: admin / admin123"
echo "============================================"
echo ""

python manage.py runserver
