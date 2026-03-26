from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

PROPERTIES = [
    # ── Agriculture Farms ──────────────────────────────────────────────────────
    {
        'title': '5 Acre Agriculture Land near Belagavi-Pune Highway',
        'property_type': 'agriculture',
        'price': 2500000,
        'price_negotiable': True,
        'area_sqft': 217800,
        'bedrooms': None,
        'bathrooms': None,
        'description': 'Fertile black soil agricultural land with bore well and electricity connection. '
                       'Ideal for sugarcane, groundnut and vegetable farming. '
                       'Located on the highway with easy access. Clear title with 7/12 extract available.',
        'address': 'Survey No. 142, Shirguppi Village, Belagavi-Pune Highway, Belagavi',
        'locality': 'Shirguppi',
        'city': 'Belagavi',
        'pincode': '590010',
        'lat': 15.9200,
        'lng': 74.5800,
        'amenities': [],
    },
    {
        'title': '2 Acre Farm with Drip Irrigation — Kakati Road',
        'property_type': 'agriculture',
        'price': 1200000,
        'price_negotiable': True,
        'area_sqft': 87120,
        'bedrooms': None,
        'bathrooms': None,
        'description': 'Well-maintained farm with drip irrigation system, mango and coconut trees. '
                       'Has small farm house, storage shed and 24/7 water supply from canal. '
                       'Perfect for organic farming. All documents clear.',
        'address': 'Survey No. 88, Kakati Village, Kakati Road, Belagavi',
        'locality': 'Kakati',
        'city': 'Belagavi',
        'pincode': '591143',
        'lat': 15.8900,
        'lng': 74.6100,
        'amenities': [],
    },

    # ── Plots ──────────────────────────────────────────────────────────────────
    {
        'title': '30×40 Residential Plot in Tilakwadi — BDA Approved',
        'property_type': 'plot',
        'price': 1800000,
        'price_negotiable': True,
        'area_sqft': 1200,
        'bedrooms': None,
        'bathrooms': None,
        'description': 'BDA approved residential plot in the heart of Tilakwadi. '
                       'Corner site with two road access. Water, drainage and electricity lines available. '
                       'Walking distance from schools and hospitals. NA order obtained.',
        'address': 'Plot No. 45, Sector 3, Tilakwadi Layout, Belagavi',
        'locality': 'Tilakwadi',
        'city': 'Belagavi',
        'pincode': '590006',
        'lat': 15.8570,
        'lng': 74.5010,
        'amenities': [],
    },
    {
        'title': '50×80 Commercial Plot — Khanapur Road Main Junction',
        'property_type': 'plot',
        'price': 4500000,
        'price_negotiable': False,
        'area_sqft': 4000,
        'bedrooms': None,
        'bathrooms': None,
        'description': 'Premium commercial plot on main Khanapur Road junction with very high footfall. '
                       'Suitable for showroom, hospital or commercial complex. '
                       'Zone: Commercial — no conversion required. Immediate registration possible.',
        'address': 'Survey No. 210, Khanapur Road Junction, Near Bus Stand, Belagavi',
        'locality': 'Khanapur Road',
        'city': 'Belagavi',
        'pincode': '590001',
        'lat': 15.8650,
        'lng': 74.5150,
        'amenities': [],
    },
    {
        'title': '20×30 Plot in Gokul Road Layout — Gated Community',
        'property_type': 'plot',
        'price': 950000,
        'price_negotiable': True,
        'area_sqft': 600,
        'bedrooms': None,
        'bathrooms': None,
        'description': 'Approved residential plot inside a secured gated community with 24/7 security. '
                       'Wide internal roads, underground drainage, streetlights and parks. '
                       'Ideal for budget home construction. Loan facility available.',
        'address': 'Plot 12, Shree Sai Layout, Gokul Road, Belagavi',
        'locality': 'Gokul Road',
        'city': 'Belagavi',
        'pincode': '590006',
        'lat': 15.8750,
        'lng': 74.4900,
        'amenities': [],
    },

    # ── Flats ──────────────────────────────────────────────────────────────────
    {
        'title': '2 BHK Flat in Shastri Nagar — Ready to Move',
        'property_type': 'flat',
        'price': 3200000,
        'price_negotiable': True,
        'area_sqft': 1050,
        'bedrooms': 2,
        'bathrooms': 2,
        'description': 'Spacious 2 BHK flat on the 3rd floor with excellent natural light and cross ventilation. '
                       'Modular kitchen, marble flooring, wooden wardrobes in all bedrooms. '
                       'Covered car parking included. Society has lift, generator backup and CCTV.',
        'address': 'Flat 304, Shree Residency, Shastri Nagar, Belagavi',
        'locality': 'Shastri Nagar',
        'city': 'Belagavi',
        'pincode': '590001',
        'lat': 15.8510,
        'lng': 74.4960,
        'amenities': ['parking', 'lift', 'security', 'power_backup'],
    },
    {
        'title': '3 BHK Premium Flat — Camp Area, Belagavi',
        'property_type': 'flat',
        'price': 5800000,
        'price_negotiable': False,
        'area_sqft': 1650,
        'bedrooms': 3,
        'bathrooms': 3,
        'description': 'Luxurious 3 BHK flat in the prestigious Camp area of Belagavi. '
                       'Italian marble flooring, premium fittings, large balcony with city view. '
                       'Two covered parking spots. Building has rooftop garden, gym and community hall. '
                       'Walking distance from major schools, hospitals and MG Road.',
        'address': 'Flat 802, Emerald Heights, Residency Road, Camp, Belagavi',
        'locality': 'Camp',
        'city': 'Belagavi',
        'pincode': '590001',
        'lat': 15.8480,
        'lng': 74.5050,
        'amenities': ['parking', 'lift', 'gym', 'security', 'power_backup', 'water_24x7'],
    },
    {
        'title': '1 BHK Flat — Vadgaon, Near Visvesvaraya Engineering College',
        'property_type': 'flat',
        'price': 1600000,
        'price_negotiable': True,
        'area_sqft': 620,
        'bedrooms': 1,
        'bathrooms': 1,
        'description': 'Affordable 1 BHK flat ideal for students and young professionals. '
                       'Fully tiled, good ventilation. On the ground floor. '
                       'Close to engineering college, medical college and bus stop. '
                       'Society maintenance ₹500/month.',
        'address': 'Flat 102, Laxmi Apartments, Vadgaon, Belagavi',
        'locality': 'Vadgaon',
        'city': 'Belagavi',
        'pincode': '590005',
        'lat': 15.8800,
        'lng': 74.5300,
        'amenities': ['water_24x7'],
    },

    # ── Rent ───────────────────────────────────────────────────────────────────
    {
        'title': '2 BHK Flat for Rent — Tilakwadi, ₹12,000/month',
        'property_type': 'rent',
        'price': 12000,
        'price_negotiable': True,
        'area_sqft': 980,
        'bedrooms': 2,
        'bathrooms': 2,
        'description': 'Well-maintained 2 BHK flat available for rent on 2nd floor. '
                       'Semi-furnished with fans, lights and kitchen chimney. '
                       'Society has 24/7 water supply and lift. '
                       'Preference: working professionals or small family. No broker fee.',
        'address': 'Flat 201, Krishna Towers, Tilakwadi, Belagavi',
        'locality': 'Tilakwadi',
        'city': 'Belagavi',
        'pincode': '590006',
        'lat': 15.8560,
        'lng': 74.5000,
        'amenities': ['lift', 'water_24x7', 'power_backup'],
    },
    {
        'title': 'Commercial Shop for Rent — Kirloskar Road, 450 sqft',
        'property_type': 'rent',
        'price': 18000,
        'price_negotiable': True,
        'area_sqft': 450,
        'bedrooms': None,
        'bathrooms': 1,
        'description': 'Ground floor shop space on busy Kirloskar Road with excellent visibility. '
                       'Suitable for retail, pharmacy, grocery or bank branch. '
                       'Has 3-phase power connection and shutters. '
                       'Available immediately. 11-month agreement.',
        'address': 'Shop No. 4, Ground Floor, Kirloskar Road, Near Post Office, Belagavi',
        'locality': 'Kirloskar Road',
        'city': 'Belagavi',
        'pincode': '590002',
        'lat': 15.8620,
        'lng': 74.5080,
        'amenities': ['power_backup'],
    },
    {
        'title': '1 BHK Furnished Room for Rent — Camp, ₹7,500/month',
        'property_type': 'rent',
        'price': 7500,
        'price_negotiable': False,
        'area_sqft': 400,
        'bedrooms': 1,
        'bathrooms': 1,
        'description': 'Fully furnished 1 BHK room with attached bathroom in a safe, quiet area of Camp. '
                       'Includes bed, wardrobe, sofa, TV, fridge and WiFi. '
                       'Suitable for single working professional or student. '
                       'No deposit, advance 2 months. Meals available from landlord on extra charge.',
        'address': '12/A, Near St. Mary\'s School, Camp, Belagavi',
        'locality': 'Camp',
        'city': 'Belagavi',
        'pincode': '590001',
        'lat': 15.8490,
        'lng': 74.5060,
        'amenities': ['water_24x7', 'power_backup'],
    },
]


class Command(BaseCommand):
    help = 'Seed dummy properties for seller_ravi in draft status'

    def handle(self, *args, **options):
        from properties.models import Property

        try:
            seller = User.objects.get(username='seller_ravi')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('seller_ravi not found. Run seed_test_users first.'))
            return

        if Property.objects.filter(owner=seller).exists():
            self.stdout.write(self.style.WARNING('Properties already exist for seller_ravi. Skipping.'))
            return

        self.stdout.write(self.style.MIGRATE_HEADING(f'\nCreating {len(PROPERTIES)} properties for seller_ravi...\n'))

        counts = {}
        for data in PROPERTIES:
            prop = Property.objects.create(
                owner=seller,
                status='approved',
                **data,
            )
            t = data['property_type']
            counts[t] = counts.get(t, 0) + 1
            self.stdout.write(f'  ✓  [{t.upper():<12}]  {data["title"][:60]}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Done!'))
        for ptype, count in counts.items():
            self.stdout.write(f'  {ptype:<14} {count} listing(s)')
        self.stdout.write(f'\n  Total: {len(PROPERTIES)} properties created (status = draft)')
        self.stdout.write('  Login as seller_ravi and submit them for verification.\n')
