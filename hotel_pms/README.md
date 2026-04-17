# Breeze PMS - Hotel Property Management System

A full-featured Django web app for managing hotel operations, built for Aryatara Kathmandu Hotel in Thamel.

## Features

- Room management with real-time status
- Reservation lifecycle (pending → confirmed → checked-in → checked-out)
- Guest profiles with VIP and blacklist flags
- Billing with invoices and payments (13% Nepal VAT)
- Maintenance ticketing
- **OTA email parsing** for Agoda, Booking.com, Trip.com, MakeMyTrip
- **Gmail auto-ingestion** — emails parse automatically
- **Pricing rules engine** with seasonal adjustments
- Dashboard with occupancy and recommended rate

## Quick Start

### Prerequisites
- Python 3.10
- PostgreSQL 14+ (or use SQLite for quick demo)
- A Gmail account with App Password (for OTA auto-ingestion)

### 1. Clone and install

```bash
git clone https://github.com/Bishw0/Breeze_PMS.git
cd Breeze_PMS/hotel_pms
pip install -r requirements.txt
```

### 2. Set up environment variables

Create a `.env` file in the `hotel_pms/` folder:
GMAIL_ADDRESS=your-gmail@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password

Get an App Password at: https://myaccount.google.com/apppasswords

### 3. Set up the database

For PostgreSQL (recommended):

```bash
createdb breeze_pms
# Update DATABASES in hotel_pms/settings.py with your Postgres user
python manage.py migrate
python manage.py seed_data
```

### 4. Run the app

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 and log in:
- **Admin:** admin / admin123
- **Receptionist:** reception / reception123

## Demo the Features

### OTA Inbox (manual)
1. Go to OTA Inbox in the sidebar
2. Paste a raw booking email
3. Click "Parse Email" — see it extract guest, dates, room, amount

### OTA Auto-Ingest from Gmail
```bash
python manage.py fetch_ota_emails
```
Fetches all unread OTA emails from your Gmail inbox and parses them automatically.

### Dashboard
See occupancy rate, recommended nightly rate (NPR) based on real pricing rules, today's arrivals/departures.

## Project Structure
hotel_pms/
├── rooms/           # Rooms, room types, maintenance
├── guests/          # Guest profiles
├── reservations/    # Bookings + pricing rules
├── billing/         # Invoices + payments
├── staff/           # Staff accounts + roles
├── ota/             # OTA email parsing (Agoda, Booking.com, Trip.com, MakeMyTrip)
└── templates/       # Bootstrap 5 HTML templates

## Tech Stack

- Django 4.2
- PostgreSQL
- Bootstrap 5
- Python 3.12
- Gmail IMAP for OTA ingestion