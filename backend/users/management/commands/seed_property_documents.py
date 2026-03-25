"""
Seed dummy documents for seller_ravi's properties so they can be submitted
for verification without needing real file uploads.

Documents are created directly in the DB with a publicly accessible dummy
PDF URL. No S3 or file-upload required.
"""
import hashlib
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

# A real, publicly accessible dummy PDF (1-page blank) — used for all docs
DUMMY_PDF_URL = 'https://www.w3.org/WAI/WCAG21/Techniques/pdf/sample.pdf'
DUMMY_S3_KEY  = 'seed/dummy_document.pdf'
DUMMY_SIZE    = 12345  # bytes
DUMMY_MIME    = 'application/pdf'
DUMMY_CHECKSUM = hashlib.sha256(b'seed-dummy-document').hexdigest()

# doc_type assigned per property type (realistic mapping)
DOCS_BY_TYPE = {
    'agriculture': [('rtc', 'RTC_Pahani.pdf'), ('ec', 'EC_Certificate.pdf')],
    'plot':        [('ec', 'EC_Certificate.pdf'), ('sale_deed', 'Sale_Deed.pdf')],
    'flat':        [('khata', 'Khata_Certificate.pdf'), ('plan_approval', 'Plan_Approval.pdf')],
    'rent':        [('tax_receipt', 'Tax_Receipt.pdf')],
}


class Command(BaseCommand):
    help = 'Seed dummy documents for seller_ravi properties (enables Submit for Verification)'

    def handle(self, *args, **options):
        from properties.models import Property
        from documents.models import Document

        try:
            seller = User.objects.get(username='seller_ravi')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('seller_ravi not found. Run seed_test_users first.'))
            return

        properties = list(Property.objects.filter(owner=seller).order_by('property_type', 'created_at'))
        if not properties:
            self.stdout.write(self.style.ERROR('No properties found for seller_ravi. Run seed_properties first.'))
            return

        self.stdout.write(self.style.MIGRATE_HEADING(
            f'\nAdding dummy documents to {len(properties)} properties...\n'
        ))

        total = 0
        for prop in properties:
            existing = prop.documents.count()
            if existing > 0:
                self.stdout.write(f'  –  [{prop.property_type.upper():<12}]  {prop.title[:52]}  (already has {existing} doc(s), skipped)')
                continue

            doc_specs = DOCS_BY_TYPE.get(prop.property_type, [('other', 'Document.pdf')])
            for doc_type, file_name in doc_specs:
                Document.objects.create(
                    property=prop,
                    doc_type=doc_type,
                    s3_key=DUMMY_S3_KEY,
                    file_url=DUMMY_PDF_URL,
                    file_name=file_name,
                    file_size=DUMMY_SIZE,
                    mime_type=DUMMY_MIME,
                    checksum=DUMMY_CHECKSUM,
                )
                total += 1

            self.stdout.write(
                f'  ✓  [{prop.property_type.upper():<12}]  {prop.title[:52]}'
                f'  ({len(doc_specs)} doc(s) added)'
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! {total} dummy document(s) added across {len(properties)} properties.'
        ))
        self.stdout.write('  All draft listings are now ready to "Submit for Verification".\n')
