from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

USERS = [
    {
        'username': 'superadmin',
        'email': 'admin@propconnect.in',
        'password': 'Admin@1234',
        'first_name': 'Super',
        'last_name': 'Admin',
        'phone': '9000000001',
        'role': 'seller',
        'is_staff': True,
        'is_superuser': True,
        'is_phone_verified': True,
        'label': 'Superadmin (Django Admin)',
    },
    {
        'username': 'seller_ravi',
        'email': 'ravi.seller@propconnect.in',
        'password': 'Seller@1234',
        'first_name': 'Ravi',
        'last_name': 'Kulkarni',
        'phone': '9000000002',
        'role': 'seller',
        'is_staff': False,
        'is_superuser': False,
        'is_phone_verified': True,
        'label': 'Seller / Property Owner',
    },
    {
        'username': 'advocate_priya',
        'email': 'priya.advocate@propconnect.in',
        'password': 'Advocate@1234',
        'first_name': 'Priya',
        'last_name': 'Desai',
        'phone': '9000000003',
        'role': 'advocate',
        'is_staff': False,
        'is_superuser': False,
        'is_phone_verified': True,
        'label': 'Advocate (Verifier)',
    },
    {
        'username': 'buyer_amit',
        'email': 'amit.buyer@propconnect.in',
        'password': 'Buyer@1234',
        'first_name': 'Amit',
        'last_name': 'Patil',
        'phone': '9000000004',
        'role': 'buyer',
        'is_staff': False,
        'is_superuser': False,
        'is_phone_verified': True,
        'label': 'Customer / Buyer',
    },
]


class Command(BaseCommand):
    help = 'Seed test users: superadmin, seller, advocate, buyer'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\nSeeding test users...\n'))

        for data in USERS:
            label = data.pop('label')
            username = data['username']
            email = data['email']
            password = data.pop('password')

            if User.objects.filter(username=username).exists():
                self.stdout.write(f'  SKIP  {label} ({email}) — already exists')
                data['label'] = label  # restore for next iteration safety
                continue

            user = User(
                username=username,
                email=email,
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data['phone'],
                role=data['role'],
                is_staff=data['is_staff'],
                is_superuser=data['is_superuser'],
                is_phone_verified=data['is_phone_verified'],
            )
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f'  OK    {label}')
                + f'  username={username}  password={password}'
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Done. Login credentials:'))
        self.stdout.write('')
        self.stdout.write('  Role       Username          Password       Email')
        self.stdout.write('  ─────────  ────────────────  ─────────────  ──────────────────────────────')
        self.stdout.write('  Superadmin superadmin        Admin@1234     admin@propconnect.in')
        self.stdout.write('  Seller     seller_ravi       Seller@1234    ravi.seller@propconnect.in')
        self.stdout.write('  Advocate   advocate_priya    Advocate@1234  priya.advocate@propconnect.in')
        self.stdout.write('  Buyer      buyer_amit        Buyer@1234     amit.buyer@propconnect.in')
        self.stdout.write('')
        self.stdout.write('  Django admin: http://127.0.0.1:8000/admin/')
        self.stdout.write('  API docs:     http://127.0.0.1:8000/api/docs/')
        self.stdout.write('')
