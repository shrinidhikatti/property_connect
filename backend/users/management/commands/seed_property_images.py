from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

BASE  = 'https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w={w}&h={h}&fit=crop'

def img(photo_id):
    return BASE.format(id=photo_id, w=800, h=500)

def thumb(photo_id):
    return BASE.format(id=photo_id, w=400, h=250)


# Pexels photo IDs — verified 200, visually relevant to each property type
# Subject confirmed: agriculture=green farmland, plot=empty land/construction,
#                    flat=apartment building/interior, rent=furnished room/shop
IMAGES_BY_TYPE = {

    # ── Agriculture Farm ──────────────────────────────────────────────────────
    # Green crop fields, irrigation, rural farmland
    'agriculture': [
        [440731,   974314,  2132180],   # green farmland, crop rows, aerial field
        [1595104,  1359557, 2280551],   # farmland field, agriculture land, rural
    ],

    # ── Plot ──────────────────────────────────────────────────────────────────
    # Empty residential / commercial plots, open land, construction sites
    'plot': [
        [209251,  1029614, 1396122],    # empty land, construction site, open plot
        [2219024, 2101137, 1474580],    # vacant land, boundary site, layout land
        [1534411, 2310454, 1662726],    # open flat land, plot with sky, clear site
    ],

    # ── Flat / Apartment ─────────────────────────────────────────────────────
    # Apartment building exteriors, living rooms, bedrooms, kitchens
    'flat': [
        [1571460, 1918291, 271624],     # apartment building, living room, bedroom
        [2062426, 1643383, 3935352],    # modern apartment, cozy flat, luxury flat
        [2724749, 276724,  1080696],    # flat interior, kitchen, bathroom modern
    ],

    # ── Rent ─────────────────────────────────────────────────────────────────
    # Furnished rental rooms, studio interiors, commercial shops
    'rent': [
        [1454806, 2062426, 271624],     # furnished room, rental interior, bedroom
        [462235,  1080721, 3183183],    # shop space, commercial interior, store front
        [1643383, 3935352, 1918291],    # studio furnished, compact flat, living area
    ],
}


class Command(BaseCommand):
    help = 'Replace property images of seller_ravi with relevant Pexels photos'

    def handle(self, *args, **options):
        from properties.models import Property, PropertyImage

        try:
            seller = User.objects.get(username='seller_ravi')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('seller_ravi not found.'))
            return

        properties = list(
            Property.objects.filter(owner=seller).order_by('property_type', 'created_at')
        )
        if not properties:
            self.stdout.write(self.style.ERROR('No properties found. Run seed_properties first.'))
            return

        # Wipe all previous images
        deleted, _ = PropertyImage.objects.filter(property__owner=seller).delete()
        self.stdout.write(self.style.MIGRATE_HEADING(
            f'\nCleared {deleted} old image(s). Adding relevant photos...\n'
        ))

        type_index = {}
        total = 0

        for prop in properties:
            ptype = prop.property_type
            idx = type_index.get(ptype, 0)
            sets = IMAGES_BY_TYPE.get(ptype, [[1571460, 1918291, 271624]])
            photo_ids = sets[idx % len(sets)]
            type_index[ptype] = idx + 1

            for order, pid in enumerate(photo_ids):
                PropertyImage.objects.create(
                    property=prop,
                    image_url=img(pid),
                    thumbnail_url=thumb(pid),
                    order=order,
                )

            total += len(photo_ids)
            self.stdout.write(
                f'  ✓  [{ptype.upper():<12}]  {prop.title[:52]}'
                f'  ({len(photo_ids)} photos)'
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! {total} relevant images set across {len(properties)} properties.'
        ))
