"""
Management command to seed the database with sample hotel data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rooms.models import Room, RoomType
from guests.models import Guest
from reservations.models import Reservation, RoomServiceItem
from staff.models import StaffProfile
import datetime


class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@hotel.com', 'admin123')
            admin.first_name = 'Admin'
            admin.last_name = 'User'
            admin.save()
            StaffProfile.objects.create(user=admin, role='admin')
            self.stdout.write('  Created admin user (admin/admin123)')

        # Receptionist
        if not User.objects.filter(username='reception').exists():
            rec = User.objects.create_user('reception', 'reception@hotel.com', 'reception123')
            rec.first_name = 'Jane'
            rec.last_name = 'Smith'
            rec.save()
            StaffProfile.objects.create(user=rec, role='receptionist', phone='+1-555-0101')

        # Room Types
        types_data = [
            ('Standard Room', 89.00, 2, 'WiFi, TV, Private Bathroom, Air Conditioning, Mini Fridge'),
            ('Deluxe Room', 129.00, 2, 'WiFi, Smart TV, King Bed, Desk, Coffee Maker, Mini Bar'),
            ('Superior Room', 159.00, 3, 'WiFi, Smart TV, Sofa Bed, Bathtub, Work Desk, Mini Bar'),
            ('Junior Suite', 219.00, 4, 'WiFi, Smart TV, Living Area, Kitchenette, Jacuzzi, Balcony'),
            ('Executive Suite', 349.00, 4, 'WiFi, Smart TV, Separate Living Room, Full Kitchen, Dining Area, Jacuzzi, Panoramic View'),
            ('Presidential Suite', 599.00, 6, 'WiFi, Multiple TVs, 2 Bedrooms, Full Kitchen, Private Bar, Butler Service, Private Terrace'),
        ]
        room_types = {}
        for name, price, cap, amenities in types_data:
            rt, _ = RoomType.objects.get_or_create(
                name=name,
                defaults={'base_price': price, 'capacity': cap, 'amenities': amenities}
            )
            room_types[name] = rt

        # Rooms
        rooms_data = [
            # Floor 1 - Standard
            ('101', 'Standard Room', 1), ('102', 'Standard Room', 1), ('103', 'Standard Room', 1),
            ('104', 'Standard Room', 1), ('105', 'Deluxe Room', 1),
            # Floor 2 - Deluxe
            ('201', 'Deluxe Room', 2), ('202', 'Deluxe Room', 2), ('203', 'Superior Room', 2),
            ('204', 'Superior Room', 2), ('205', 'Deluxe Room', 2),
            # Floor 3 - Superior/Suite
            ('301', 'Superior Room', 3), ('302', 'Superior Room', 3),
            ('303', 'Junior Suite', 3), ('304', 'Junior Suite', 3),
            # Floor 4 - Suites
            ('401', 'Executive Suite', 4), ('402', 'Executive Suite', 4),
            ('403', 'Junior Suite', 4),
            # Penthouse
            ('501', 'Presidential Suite', 5),
        ]
        for number, type_name, floor in rooms_data:
            Room.objects.get_or_create(
                number=number,
                defaults={
                    'room_type': room_types[type_name],
                    'floor': floor,
                    'status': 'available',
                    'has_view': floor >= 3,
                }
            )

        # Service Items
        services = [
            ('Room Service Breakfast', 'food', 25.00),
            ('Room Service Lunch', 'food', 35.00),
            ('Room Service Dinner', 'food', 45.00),
            ('Mini Bar Restock', 'food', 30.00),
            ('Laundry - Regular', 'laundry', 15.00),
            ('Laundry - Express', 'laundry', 25.00),
            ('Spa - 60min Massage', 'spa', 90.00),
            ('Spa - Facial Treatment', 'spa', 75.00),
            ('Airport Transfer', 'transport', 40.00),
            ('Late Check-out Fee', 'other', 50.00),
            ('Extra Bed', 'other', 35.00),
        ]
        for name, cat, price in services:
            RoomServiceItem.objects.get_or_create(name=name, defaults={'category': cat, 'price': price})

        # Guests
        guests_data = [
            ('John', 'Smith', 'john.smith@email.com', '+1-555-0101', 'American', False),
            ('Emma', 'Johnson', 'emma.j@email.com', '+44-20-5555-0102', 'British', True),
            ('Carlos', 'Rodriguez', 'carlos.r@email.com', '+34-91-555-0103', 'Spanish', False),
            ('Yuki', 'Tanaka', 'yuki.t@email.com', '+81-3-5555-0104', 'Japanese', True),
            ('Sophie', 'Müller', 'sophie.m@email.com', '+49-30-555-0105', 'German', False),
            ('Ahmed', 'Al-Rashid', 'ahmed.ar@email.com', '+971-4-555-0106', 'Emirati', True),
            ('Priya', 'Sharma', 'priya.s@email.com', '+91-98-5555-0107', 'Indian', False),
            ('Lucas', 'Petit', 'lucas.p@email.com', '+33-1-5555-0108', 'French', False),
        ]
        created_guests = []
        for fn, ln, email, phone, nat, vip in guests_data:
            g, _ = Guest.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': fn, 'last_name': ln, 'phone': phone,
                    'nationality': nat, 'vip_status': vip,
                }
            )
            created_guests.append(g)

        # Sample Reservations
        today = datetime.date.today()
        admin_user = User.objects.get(username='admin')
        rooms = list(Room.objects.all())

        reservations_data = [
            (created_guests[0], rooms[0], today - datetime.timedelta(days=2), today + datetime.timedelta(days=1), 'checked_in'),
            (created_guests[1], rooms[5], today, today + datetime.timedelta(days=3), 'confirmed'),
            (created_guests[2], rooms[12], today + datetime.timedelta(days=1), today + datetime.timedelta(days=4), 'confirmed'),
            (created_guests[3], rooms[14], today - datetime.timedelta(days=5), today - datetime.timedelta(days=1), 'checked_out'),
            (created_guests[4], rooms[2], today + datetime.timedelta(days=3), today + datetime.timedelta(days=7), 'confirmed'),
            (created_guests[5], rooms[17], today - datetime.timedelta(days=1), today + datetime.timedelta(days=2), 'checked_in'),
        ]

        for guest, room, checkin, checkout, status in reservations_data:
            if not Reservation.objects.filter(guest=guest, check_in=checkin).exists():
                res = Reservation.objects.create(
                    guest=guest, room=room, check_in=checkin, check_out=checkout,
                    status=status, adults=2, rate_per_night=room.current_price,
                    source='direct', created_by=admin_user,
                )
                if status == 'checked_in':
                    res.actual_check_in = datetime.datetime.now() - datetime.timedelta(hours=3)
                    res.save()
                    room.status = 'occupied'
                    room.save()
                elif status == 'confirmed':
                    room.status = 'reserved'
                    room.save()

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin:       admin / admin123')
        self.stdout.write('  Receptionist: reception / reception123')
