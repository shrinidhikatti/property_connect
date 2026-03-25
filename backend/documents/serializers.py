from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    doc_type_display = serializers.CharField(source='get_doc_type_display', read_only=True)

    class Meta:
        model = Document
        fields = (
            'id', 'doc_type', 'doc_type_display', 'file_name',
            'file_size', 'mime_type', 'uploaded_at',
        )
        # s3_key and checksum are never exposed to clients
