# 🏨 Hotel Property Management System (PMS)

A full-featured Django web application for managing hotel operations — built with Django 4.2, Bootstrap 5, and SQLite.

---

## Features

### 🏠 Room Management
- Room grid with real-time status (Available, Occupied, Cleaning, Maintenance, Reserved)
- Room types with pricing, capacity, and amenities
- One-click status updates
- Floor and type filtering

### 📅 Reservations
- Full booking lifecycle: Pending → Confirmed → Checked In → Checked Out
- Conflict detection — prevents double-bookings
- Multi-source tracking (Walk-in, Phone, OTA, Corporate, etc.)
- Special requests and internal notes
- Service charge attachment during stays

### 👥 Guest Management
- Comprehensive guest profiles with contact info, ID, address
- VIP flagging and blacklist management
- Full stay history and total spend tracking
- Quick search by name, email, or phone

### 💳 Billing & Invoicing
- Auto-generated invoices on checkout
- Itemised line items: room charges + service charges
- Tax calculation (configurable rate)
- Payment recording with multiple methods (Cash, Card, Bank Transfer)
- Partial payment tracking and balance due
- Revenue reports with 30-day chart

### 🔧 Maintenance
- Maintenance request ticketing system
- Priority levels: Low / Medium / High / Urgent
- Status workflow: Open → In Progress → Resolved → Closed
- Auto-sets room to "Maintenance" on creation, "Cleaning" on resolve

### 👔 Staff
- Staff profiles with roles (Admin, Manager, Receptionist, Housekeeping, etc.)
- Django auth integration with login/logout
- Per-role access ready to extend with permissions

---

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
cd hotel_pms

# Option 1: Use the setup script
chmod +x start.sh
./start.sh

# Option 2: Manual setup
pip install -r requirements.txt
python manage.py makemigrations rooms guests reservations billing staff
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Then open **http://127.0.0.1:8000** in your browser.

### Default Credentials

| Role         | Username    | Password       |
|--------------|-------------|----------------|
| Admin        | `admin`     | `admin123`     |
| Receptionist | `reception` | `reception123` |

---

## Project Structure

```
hotel_pms/
├── hotel_pms/          # Django project config
│   ├── settings.py
│   └── urls.py
│
├── rooms/              # Room & maintenance management
│   ├── models.py       # Room, RoomType, MaintenanceRequest
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── guests/             # Guest profiles
│   ├── models.py       # Guest
│   ├── views.py
│   └── forms.py
│
├── reservations/       # Bookings & service charges
│   ├── models.py       # Reservation, ServiceCharge, RoomServiceItem
│   ├── views.py        # Dashboard, check-in/out, charges
│   └── forms.py
│
├── billing/            # Invoices & payments
│   ├── models.py       # Invoice, Payment
│   ├── views.py        # Invoice list, detail, payments, revenue report
│   └── forms.py
│
├── staff/              # Staff accounts
│   ├── models.py       # StaffProfile, ShiftLog
│   ├── views.py        # Login, logout, staff management
│   └── forms.py
│
└── templates/          # HTML templates (Bootstrap 5)
    ├── base.html
    ├── dashboard/
    ├── rooms/
    ├── reservations/
    ├── guests/
    ├── billing/
    └── staff/
```

---

## Data Models

```
RoomType ──< Room
Guest ──< Reservation >── Room
Reservation ──< ServiceCharge >── RoomServiceItem
Reservation ──1 Invoice ──< Payment
User ──1 StaffProfile
Room ──< MaintenanceRequest
```

---

## Extending the System

### Add permissions by role
In `views.py`, use `@user_passes_test` or a custom decorator:
```python
from django.contrib.auth.decorators import user_passes_test

def is_manager(user):
    return hasattr(user, 'staff_profile') and user.staff_profile.role in ['admin', 'manager']

@user_passes_test(is_manager)
def revenue_report(request):
    ...
```

### Production deployment
1. Set `DEBUG = False` in `settings.py`
2. Set a strong `SECRET_KEY`
3. Configure PostgreSQL in `DATABASES`
4. Run `python manage.py collectstatic`
5. Use `gunicorn` + `nginx`

---

## Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Backend   | Django 4.2              |
| Database  | SQLite (dev) / PostgreSQL (prod) |
| Frontend  | Bootstrap 5.3 + Bootstrap Icons |
| Charts    | Chart.js 4.4            |
| Auth      | Django built-in auth    |
