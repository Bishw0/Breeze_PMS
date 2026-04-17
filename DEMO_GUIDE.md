# Breeze PMS - Demo Guide for Aryatara Kathmandu Hotel

This guide walks the developer through demoing Breeze PMS to hotel staff.

## Before the Meeting

1. Pull latest code:

```bash
git pull origin main
```

2. Make sure app runs locally:

```bash
cd hotel_pms
python manage.py runserver
```

3. Open http://127.0.0.1:8000 and verify login works with `admin / admin123`

4. Have a test OTA email ready to parse live during the demo (use the Booking.com sample)

## Demo Flow (15 minutes)

### 1. Introduction (1 min)

"This is Breeze PMS - a property management system built specifically for Thamel hotels. Everything you see runs in your browser, no installation needed."

### 2. Dashboard Walkthrough (3 min)

- **Occupancy Rate** — live count of occupied rooms
- **Today's Arrivals/Departures** — what the front desk needs each morning
- **Recommended Rate Tonight** — NPR rate suggestion based on occupancy and active pricing rules
- **Recent Reservations** — quick access to active bookings

### 3. OTA Inbox - The Killer Feature (5 min)

"This is what saves you the most time every day."

**Show manual parsing:**

- Go to OTA Inbox
- Paste a Booking.com email
- Watch it extract guest name, dates, room, amount automatically

**Show auto-ingestion:**

- Explain: "When you connect your hotel's Gmail, every new OTA booking parses automatically"
- Run `python manage.py fetch_ota_emails` to show it working live
- Show the newly parsed email in the inbox

### 4. Reservations & Check-in (2 min)

- Show a reservation detail
- Demonstrate check-in / check-out buttons
- Show how status changes update room availability

### 5. Billing (2 min)

- Show an invoice
- Point out: automatic 13% VAT calculation
- Show payment recording (cash, card, bank transfer)

### 6. Pricing Rules (2 min)

- Show pricing rules list
- Explain: "Weekend lift, festival rates, direct booking discounts — all automatic"
- Point back to the dashboard rate card

## Questions to Ask the Hotel

1. How many bookings per day do you typically handle via Booking.com / Agoda?
2. Who at the hotel needs access? (admin, receptionist, manager?)
3. Do you want us to connect your actual Gmail or create a dedicated hotel Gmail?
4. What's your biggest pain point today with bookings and reservations?
5. What's your current system? (paper, Excel, another PMS?)

## Closing

"If you'd like to try this, we can have it live on a web address for your staff within 48 hours. Monthly cost would be NPR 2,500 - that includes hosting, updates, and support."

## Technical Notes for Kumud

- App is Django 4.2 + PostgreSQL + Bootstrap 5
- All code: github.com/Bishw0/Breeze_PMS
- OTA parsers work for: Agoda, Booking.com, Trip.com, MakeMyTrip
- Gmail IMAP with App Password is already configured
- Dashboard shows live data, not mock
