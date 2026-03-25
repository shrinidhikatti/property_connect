from django.db import migrations


PLANS = [
    {'code': 'free',    'name': 'Free',    'description': 'Get started with 1 active listing.',                         'price_paise': 0,      'listing_limit': 1,  'validity_days': 30, 'is_featured_included': False, 'is_active': True, 'sort_order': 0},
    {'code': 'basic',   'name': 'Basic',   'description': 'Up to 5 active listings for individual sellers.',             'price_paise': 49900,  'listing_limit': 5,  'validity_days': 30, 'is_featured_included': False, 'is_active': True, 'sort_order': 1},
    {'code': 'pro',     'name': 'Pro',     'description': 'Unlimited listings for serious sellers.',                     'price_paise': 99900,  'listing_limit': -1, 'validity_days': 30, 'is_featured_included': False, 'is_active': True, 'sort_order': 2},
    {'code': 'builder', 'name': 'Builder', 'description': 'Unlimited listings + featured placement for builders.',       'price_paise': 249900, 'listing_limit': -1, 'validity_days': 30, 'is_featured_included': True,  'is_active': True, 'sort_order': 3},
]


def seed_plans(apps, schema_editor):
    Plan = apps.get_model('payments', 'Plan')
    for data in PLANS:
        Plan.objects.get_or_create(code=data['code'], defaults=data)


def unseed_plans(apps, schema_editor):
    Plan = apps.get_model('payments', 'Plan')
    Plan.objects.filter(code__in=[p['code'] for p in PLANS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_plans, reverse_code=unseed_plans),
    ]
