import uuid
from django.db import models
from properties.models import Property


class Document(models.Model):
    DOC_TYPES = [
        ('ec', 'Encumbrance Certificate (EC)'),
        ('mother_deed', 'Mother Deed'),
        ('khata', 'Khata Certificate'),
        ('rtc', 'RTC (Pahani)'),
        ('conversion_order', 'Conversion Order'),
        ('sale_deed', 'Sale Deed'),
        ('rera_cert', 'RERA Certificate'),
        ('tax_receipt', 'Property Tax Receipt'),
        ('plan_approval', 'Building Plan Approval'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    s3_key = models.CharField(max_length=500)
    file_url = models.URLField()
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # bytes
    mime_type = models.CharField(max_length=100)
    checksum = models.CharField(max_length=64)  # SHA-256
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documents'
        ordering = ['uploaded_at']

    def __str__(self):
        return f'{self.get_doc_type_display()} — {self.property.title}'
